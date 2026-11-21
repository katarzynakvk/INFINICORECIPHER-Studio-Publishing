import json
from uuid import uuid4

from backend.db.database import ProjectDatabase
from backend.domain.canon import CanonLock, CanonRevision
from backend.domain.project import utc_now


class RevisionConflict(ValueError):
    pass


class CanonLocked(ValueError):
    pass


class CanonService:
    def create(
        self,
        database: ProjectDatabase,
        canon_id: str,
        payload: dict,
        locks: tuple[CanonLock, ...] = (),
    ) -> CanonRevision:
        existing = database.execute(
            "SELECT canon_id FROM canon_revisions WHERE canon_id=? LIMIT 1",
            (canon_id,),
        ).fetchone()
        if existing is not None:
            raise RevisionConflict("Canon identity already exists")
        revision = CanonRevision(canon_id, 1, None, "DRAFT", payload, locks)
        self._insert(database, revision)
        database._require_open().commit()
        return revision

    def update(
        self,
        database: ProjectDatabase,
        canon_id: str,
        expected_revision: int,
        payload: dict,
        new_locks: tuple[CanonLock, ...] | None = None,
    ) -> CanonRevision:
        current = self.get(database, canon_id)
        if current is None:
            raise KeyError("Canon revision not found")
        if current.revision != expected_revision:
            raise RevisionConflict("Stale Canon revision")
        if current.state == "LOCKED":
            raise CanonLocked("Locked Canon revisions require a successor workflow")
        if current.state == "APPROVED":
            revision_number = current.revision + 1
        else:
            revision_number = current.revision + 1
        revision = CanonRevision(
            canon_id,
            revision_number,
            current.revision,
            "DRAFT",
            payload,
            current.locks if new_locks is None else new_locks,
        )
        self._insert(database, revision)
        database._require_open().commit()
        return revision

    def approve(
        self,
        database: ProjectDatabase,
        canon_id: str,
        revision: int,
        actor_id: str,
    ) -> CanonRevision:
        current = self.get(database, canon_id)
        if current is None:
            raise KeyError("Canon revision not found")
        if current.revision != revision:
            raise RevisionConflict("Approval targets a stale revision")
        approval_id = str(uuid4())
        database.execute(
            "INSERT INTO canon_approvals(approval_id, canon_id, canon_revision, actor_id, decided_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (approval_id, canon_id, revision, actor_id, utc_now()),
        )
        database.execute(
            "UPDATE canon_revisions SET state='APPROVED' "
            "WHERE canon_id=? AND revision=?",
            (canon_id, revision),
        )
        database._require_open().commit()
        return CanonRevision(
            canon_id,
            revision,
            current.parent_revision,
            "APPROVED",
            current.payload,
            current.locks,
        )

    def lock(
        self,
        database: ProjectDatabase,
        canon_id: str,
        revision: int,
    ) -> CanonRevision:
        current = self.get(database, canon_id)
        if current is None:
            raise KeyError("Canon revision not found")
        if current.revision != revision:
            raise RevisionConflict("Lock targets a stale revision")
        if current.state != "APPROVED":
            raise CanonLocked("Canon must be APPROVED before it can be LOCKED")
        database.execute(
            "UPDATE canon_revisions SET state='LOCKED' "
            "WHERE canon_id=? AND revision=?",
            (canon_id, revision),
        )
        database._require_open().commit()
        return CanonRevision(
            canon_id,
            revision,
            current.parent_revision,
            "LOCKED",
            current.payload,
            current.locks,
        )

    def get(self, database: ProjectDatabase, canon_id: str) -> CanonRevision | None:
        row = database.execute(
            "SELECT canon_id, revision, parent_revision, state, payload_json, locks_json "
            "FROM canon_revisions WHERE canon_id=? "
            "ORDER BY revision DESC LIMIT 1",
            (canon_id,),
        ).fetchone()
        if row is None:
            return None
        return CanonRevision(
            row["canon_id"],
            int(row["revision"]),
            row["parent_revision"],
            row["state"],
            json.loads(row["payload_json"]),
            tuple(json.loads(row["locks_json"])),
        )

    def _insert(self, database: ProjectDatabase, revision: CanonRevision) -> None:
        database.execute(
            "INSERT INTO canon_revisions("
            "canon_id, revision, parent_revision, state, payload_json, locks_json, created_at"
            ") VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                revision.canon_id,
                revision.revision,
                revision.parent_revision,
                revision.state,
                json.dumps(revision.payload, ensure_ascii=False),
                json.dumps(list(revision.locks)),
                utc_now(),
            ),
        )
