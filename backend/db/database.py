import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 2


class ProjectDatabase:
    """An explicitly owned SQLite connection for one Book Project."""

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self._connection: sqlite3.Connection | None = None
        self._closed = False

    @property
    def closed(self) -> bool:
        return self._closed

    def open(self) -> "ProjectDatabase":
        if self._closed:
            raise RuntimeError("Database has been closed")
        if self._connection is None:
            self.database_path.parent.mkdir(parents=True, exist_ok=True)
            # The API serializes access across request threads; callers outside it must do the same.
            connection = sqlite3.connect(self.database_path, check_same_thread=False)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute("PRAGMA journal_mode = WAL")
            connection.execute("PRAGMA busy_timeout = 5000")
            self._connection = connection
        return self

    def initialize_schema(self) -> None:
        connection = self._require_open()
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS project_meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS migration_registry (
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                applied_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS entity_revisions (
                entity_id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL,
                revision INTEGER NOT NULL CHECK (revision >= 1),
                state TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(entity_id, revision)
            );

            CREATE TABLE IF NOT EXISTS approvals (
                approval_id TEXT PRIMARY KEY,
                entity_id TEXT NOT NULL,
                entity_revision INTEGER NOT NULL,
                actor_id TEXT NOT NULL,
                decision TEXT NOT NULL,
                decided_at TEXT NOT NULL,
                FOREIGN KEY (entity_id) REFERENCES entity_revisions(entity_id)
            );

            CREATE TABLE IF NOT EXISTS settings (
                setting_id TEXT PRIMARY KEY,
                scope TEXT NOT NULL,
                scope_id TEXT NOT NULL,
                key TEXT NOT NULL,
                value_json TEXT,
                state TEXT NOT NULL,
                revision INTEGER NOT NULL CHECK (revision >= 1),
                updated_at TEXT NOT NULL,
                UNIQUE(scope, scope_id, key)
            );

            CREATE TABLE IF NOT EXISTS canon_revisions (
                canon_id TEXT NOT NULL,
                revision INTEGER NOT NULL CHECK (revision >= 1),
                parent_revision INTEGER,
                state TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                locks_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                PRIMARY KEY(canon_id, revision),
                FOREIGN KEY(canon_id, parent_revision)
                    REFERENCES canon_revisions(canon_id, revision)
            );

            CREATE TABLE IF NOT EXISTS canon_approvals (
                approval_id TEXT PRIMARY KEY,
                canon_id TEXT NOT NULL,
                canon_revision INTEGER NOT NULL,
                actor_id TEXT NOT NULL,
                decided_at TEXT NOT NULL,
                FOREIGN KEY(canon_id, canon_revision)
                    REFERENCES canon_revisions(canon_id, revision)
            );

            CREATE TABLE IF NOT EXISTS canon_conflicts (
                conflict_id TEXT PRIMARY KEY,
                canon_id TEXT NOT NULL,
                left_revision INTEGER NOT NULL,
                right_revision INTEGER NOT NULL,
                status TEXT NOT NULL,
                detail TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        connection.execute(
            "INSERT OR IGNORE INTO project_meta(key, value) VALUES (?, ?)",
            ("schema_version", str(SCHEMA_VERSION)),
        )
        connection.execute(
            "INSERT OR IGNORE INTO migration_registry(version, name, applied_at) "
            "VALUES (?, ?, ?)",
            (1, "001_initial_project_schema", datetime.now(timezone.utc).isoformat()),
        )
        connection.execute(
            "INSERT OR IGNORE INTO migration_registry(version, name, applied_at) "
            "VALUES (?, ?, ?)",
            (2, "002_settings_and_canon_foundation", datetime.now(timezone.utc).isoformat()),
        )
        connection.commit()

    def set_meta(self, key: str, value: str) -> None:
        connection = self._require_open()
        with connection:
            connection.execute(
                "INSERT INTO project_meta(key, value) VALUES (?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, value),
            )

    def get_meta(self, key: str) -> str | None:
        row = self._require_open().execute(
            "SELECT value FROM project_meta WHERE key = ?", (key,)
        ).fetchone()
        return None if row is None else str(row["value"])

    def execute(self, sql: str, parameters: tuple[Any, ...] = ()) -> sqlite3.Cursor:
        return self._require_open().execute(sql, parameters)

    def verify_integrity(self) -> str:
        row = self._require_open().execute("PRAGMA integrity_check").fetchone()
        return str(row[0]) if row is not None else "unknown"

    def close(self) -> None:
        if self._connection is not None:
            connection = self._connection
            self._connection = None
            connection.close()
        self._closed = True

    def __enter__(self) -> "ProjectDatabase":
        return self.open()

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def _require_open(self) -> sqlite3.Connection:
        if self._closed:
            raise RuntimeError("Database has been closed")
        if self._connection is None:
            raise RuntimeError("Database is not open")
        return self._connection
