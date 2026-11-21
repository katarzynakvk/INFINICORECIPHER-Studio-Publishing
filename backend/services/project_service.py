import json
import shutil
import zipfile
from pathlib import Path

from backend.db.database import ProjectDatabase
from backend.domain.project import ProjectIdentity
from backend.repositories.project_repository import ProjectRepository
from backend.utils.filesystem import (
    atomic_write_json,
    initialize_project_directories,
    sha256_file,
)


class ProjectService:
    def __init__(self, repository: ProjectRepository | None = None) -> None:
        self.repository = repository or ProjectRepository()
        self._database: ProjectDatabase | None = None
        self._project_root: Path | None = None

    @property
    def open_project_root(self) -> Path | None:
        return self._project_root

    def create_project(self, root: Path, title: str) -> tuple[ProjectIdentity, ProjectDatabase]:
        root = root.resolve()
        if self._database is not None:
            self.close_project()
        if root.exists() and any(root.iterdir()):
            raise FileExistsError("Project destination must be empty")
        initialize_project_directories(root)
        identity = self.repository.create(root, title)
        database = ProjectDatabase(root / "project.sqlite")
        database.open()
        try:
            database.initialize_schema()
            database.set_meta("book_id", identity.book_id)
            database.set_meta("title", identity.title)
        except BaseException:
            database.close()
            raise
        self._database = database
        self._project_root = root
        return identity, database

    def open_project(self, root: Path) -> tuple[ProjectIdentity, ProjectDatabase]:
        root = root.resolve()
        identity = self.repository.read(root)
        database = ProjectDatabase(root / "project.sqlite")
        database.open()
        try:
            if database.verify_integrity() != "ok":
                raise RuntimeError("SQLite integrity check failed")
            stored_book_id = database.get_meta("book_id")
            if stored_book_id != identity.book_id:
                raise ValueError("Project manifest and database book identity differ")
        except BaseException:
            database.close()
            raise
        self.close_project()
        self._database = database
        self._project_root = root
        return identity, database

    def close_project(self) -> None:
        if self._database is not None:
            self._database.close()
            self._database = None
        self._project_root = None

    def rename_project(
        self, root: Path, title: str, expected_identity: ProjectIdentity
    ) -> ProjectIdentity:
        updated = self.repository.rename(root, title, expected_identity)
        if self._database is not None:
            self._database.set_meta("title", title)
        return updated

    def create_backup(self, root: Path) -> Path:
        root = root.resolve()
        identity = self.repository.read(root)
        database = self._database if self._project_root == root and self._database is not None else None
        database = database or ProjectDatabase(root / "project.sqlite").open()
        backup_dir = root / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_id = identity.created_at.replace(":", "-").replace(".", "-")
        staging = backup_dir / f".{identity.book_id}-{backup_id}"
        staging.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(root / "project.json", staging / "project.json")
            database.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            backup_database = ProjectDatabase(staging / "project.sqlite")
            backup_database.open()
            try:
                database._require_open().backup(backup_database._require_open())
                backup_database._require_open().commit()
                if backup_database.verify_integrity() != "ok":
                    raise RuntimeError("Backup SQLite integrity check failed")
            finally:
                backup_database.close()

            manifest = {
                "format": "INFINICORECIPHER-BACKUP",
                "format_version": 1,
                "book_id": identity.book_id,
                "project_json_sha256": sha256_file(staging / "project.json"),
                "database_sha256": sha256_file(staging / "project.sqlite"),
            }
            atomic_write_json(staging / "manifest.json", manifest)
            archive = backup_dir / f"{identity.book_id}-{backup_id}.zip"
            if archive.exists():
                raise FileExistsError("Backup already exists")
            with zipfile.ZipFile(archive, "x", zipfile.ZIP_DEFLATED) as handle:
                for path in sorted(staging.iterdir()):
                    handle.write(path, path.name)
        finally:
            shutil.rmtree(staging)
            if database is not self._database:
                database.close()
        return archive

    def restore_backup(self, archive: Path, destination: Path) -> tuple[ProjectIdentity, ProjectDatabase]:
        archive = archive.resolve()
        destination = destination.resolve()
        if destination.exists():
            raise FileExistsError("Restore destination must not exist")
        destination.mkdir(parents=True)
        staging = destination.parent / f".restore-{archive.stem}"
        if staging.exists():
            raise FileExistsError("Restore staging path already exists")
        staging.mkdir()
        try:
            with zipfile.ZipFile(archive, "r") as handle:
                allowed = {"manifest.json", "project.json", "project.sqlite"}
                for member in handle.namelist():
                    if member not in allowed or Path(member).name != member:
                        raise ValueError("Invalid or unsafe backup archive")
                handle.extractall(staging)

            manifest = json.loads((staging / "manifest.json").read_text(encoding="utf-8"))
            if manifest.get("format") != "INFINICORECIPHER-BACKUP":
                raise ValueError("Unsupported backup format")
            if sha256_file(staging / "project.json") != manifest["project_json_sha256"]:
                raise ValueError("Backup project manifest hash mismatch")
            if sha256_file(staging / "project.sqlite") != manifest["database_sha256"]:
                raise ValueError("Backup database hash mismatch")

            restored_identity = self.repository.read(staging)
            if restored_identity.book_id != manifest["book_id"]:
                raise ValueError("Backup identity mismatch")
            for name in ("project.json", "project.sqlite"):
                shutil.move(staging / name, destination / name)
            initialize_project_directories(destination)

            identity, database = self.open_project(destination)
            return identity, database
        except BaseException:
            shutil.rmtree(destination, ignore_errors=True)
            raise
        finally:
            shutil.rmtree(staging, ignore_errors=True)
