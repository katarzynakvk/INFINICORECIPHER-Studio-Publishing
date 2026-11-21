import json
import os
from pathlib import Path
from uuid import uuid4

from backend.domain.project import ProjectIdentity, utc_now
from backend.utils.filesystem import atomic_write_json


class ProjectRepository:
    def create(self, root: Path, title: str) -> ProjectIdentity:
        root.mkdir(parents=True, exist_ok=True)
        identity = ProjectIdentity(
            book_id=str(uuid4()),
            title=title,
            schema_version=1,
            created_at=utc_now(),
        )
        atomic_write_json(
            root / "project.json",
            {
                "book_id": identity.book_id,
                "title": identity.title,
                "schema_version": identity.schema_version,
                "created_at": identity.created_at,
                "state": identity.state,
            },
        )
        return identity

    def read(self, root: Path) -> ProjectIdentity:
        path = root / "project.json"
        if not path.is_file():
            raise FileNotFoundError(f"Missing project manifest: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        return ProjectIdentity(
            book_id=str(data["book_id"]),
            title=str(data["title"]),
            schema_version=int(data["schema_version"]),
            created_at=str(data["created_at"]),
            state=str(data.get("state", "ACTIVE")),
        )

    def rename(self, root: Path, title: str, expected_identity: ProjectIdentity) -> ProjectIdentity:
        current = self.read(root)
        if current.book_id != expected_identity.book_id:
            raise ValueError("Project identity changed")
        updated = ProjectIdentity(
            book_id=current.book_id,
            title=title,
            schema_version=current.schema_version,
            created_at=current.created_at,
            state=current.state,
        )
        atomic_write_json(
            root / "project.json",
            {
                "book_id": updated.book_id,
                "title": updated.title,
                "schema_version": updated.schema_version,
                "created_at": updated.created_at,
                "state": updated.state,
            },
        )
        return updated
