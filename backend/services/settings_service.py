import json
from pathlib import Path
from uuid import uuid4

from backend.db.database import ProjectDatabase
from backend.domain.project import utc_now
from backend.domain.settings import Setting, SettingScope, SettingState


class SettingsService:
    def set_setting(
        self,
        database: ProjectDatabase,
        scope: SettingScope,
        scope_id: str,
        key: str,
        value: object,
    ) -> Setting:
        current = self.get_setting(database, scope, scope_id, key)
        revision = 1 if current is None else current.revision + 1
        setting_id = str(uuid4()) if current is None else current.setting_id
        database.execute(
            "INSERT INTO settings(setting_id, scope, scope_id, key, value_json, "
            "state, revision, updated_at) VALUES (?, ?, ?, ?, ?, 'EXPLICIT', ?, ?) "
            "ON CONFLICT(scope, scope_id, key) DO UPDATE SET "
            "setting_id=excluded.setting_id, value_json=excluded.value_json, "
            "state='EXPLICIT', revision=excluded.revision, updated_at=excluded.updated_at",
            (
                setting_id,
                scope,
                scope_id,
                key,
                json.dumps(value, ensure_ascii=False),
                revision,
                utc_now(),
            ),
        )
        database._require_open().commit()
        return Setting(setting_id, scope, scope_id, key, value, "EXPLICIT", revision)

    def get_setting(
        self,
        database: ProjectDatabase,
        scope: SettingScope,
        scope_id: str,
        key: str,
    ) -> Setting | None:
        row = database.execute(
            "SELECT setting_id, scope, scope_id, key, value_json, state, revision "
            "FROM settings WHERE scope=? AND scope_id=? AND key=?",
            (scope, scope_id, key),
        ).fetchone()
        if row is None:
            return None
        value = json.loads(row["value_json"]) if row["value_json"] is not None else None
        return Setting(
            row["setting_id"],
            row["scope"],
            row["scope_id"],
            row["key"],
            value,
            row["state"],
            int(row["revision"]),
        )
