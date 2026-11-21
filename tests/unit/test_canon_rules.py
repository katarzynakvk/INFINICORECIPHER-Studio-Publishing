from pathlib import Path

import pytest

from backend.db.database import ProjectDatabase
from backend.services.canon_service import CanonLocked, CanonService, RevisionConflict
from backend.services.settings_service import SettingsService


def test_setting_explicit_revision_and_unset(tmp_path: Path) -> None:
    database = ProjectDatabase(tmp_path / "project.sqlite")
    database.open()
    database.initialize_schema()
    settings = SettingsService()

    assert settings.get_setting(database, "PROJECT", "book-1", "trim_size") is None
    first = settings.set_setting(database, "PROJECT", "book-1", "trim_size", "6x9")
    second = settings.set_setting(database, "PROJECT", "book-1", "trim_size", "7x10")

    assert first.revision == 1
    assert second.revision == 2
    assert second.state == "EXPLICIT"
    assert second.value == "7x10"
    database.close()


def test_canon_approval_lock_and_immutable_successor(tmp_path: Path) -> None:
    database = ProjectDatabase(tmp_path / "project.sqlite")
    database.open()
    database.initialize_schema()
    canon = CanonService()

    draft = canon.create(
        database,
        "character:mira",
        {"hair": "black", "height": "tall"},
        ("LOCK_CHARACTER",),
    )
    approved = canon.approve(database, draft.canon_id, draft.revision, "founder")
    assert approved.state == "APPROVED"

    locked = canon.lock(database, approved.canon_id, approved.revision)
    assert locked.state == "LOCKED"

    with pytest.raises(CanonLocked):
        canon.update(
            database,
            locked.canon_id,
            locked.revision,
            {"hair": "red", "height": "tall"},
        )

    history = database.execute(
        "SELECT revision, state FROM canon_revisions "
        "WHERE canon_id=? ORDER BY revision",
        ("character:mira",),
    ).fetchall()
    assert [(row["revision"], row["state"]) for row in history] == [
        (1, "LOCKED")
    ]
    database.close()


def test_canon_stale_mutation_is_rejected(tmp_path: Path) -> None:
    database = ProjectDatabase(tmp_path / "project.sqlite")
    database.open()
    database.initialize_schema()
    canon = CanonService()
    first = canon.create(database, "style:main", {"palette": "blue"})
    canon.update(database, first.canon_id, first.revision, {"palette": "green"})

    with pytest.raises(RevisionConflict):
        canon.update(database, first.canon_id, first.revision, {"palette": "red"})
    database.close()
