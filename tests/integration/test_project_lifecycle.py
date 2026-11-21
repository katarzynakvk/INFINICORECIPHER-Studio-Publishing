import shutil
import zipfile
from pathlib import Path

import pytest

from backend.services.project_service import ProjectService


def test_create_close_reopen_and_directory_cleanup(tmp_path: Path) -> None:
    project_root = tmp_path / "rules-for-loving-me"
    service = ProjectService()

    identity, database = service.create_project(project_root, "Rules For Loving Me")
    assert identity.book_id
    assert database.verify_integrity() == "ok"
    assert (project_root / "project.sqlite").is_file()
    database_path = project_root / "project.sqlite"

    service.close_project()
    assert database.closed
    shutil.rmtree(project_root)
    assert not database_path.exists()

    project_root = tmp_path / "later-project"
    identity, database = service.create_project(project_root, "Later Project")
    reopened_identity, reopened_database = service.open_project(project_root)
    assert reopened_identity.book_id == identity.book_id
    assert reopened_database.verify_integrity() == "ok"
    service.close_project()


def test_project_isolation_and_rename_preserve_identity(tmp_path: Path) -> None:
    service = ProjectService()
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"

    first, first_db = service.create_project(first_root, "First")
    first_db.set_meta("isolation_marker", "first-only")
    service.close_project()

    second, second_db = service.create_project(second_root, "Second")
    assert second_db.get_meta("isolation_marker") is None
    assert second.book_id != first.book_id

    renamed = service.rename_project(second_root, "Renamed", second)
    assert renamed.book_id == second.book_id
    assert renamed.title == "Renamed"
    service.close_project()


def test_schema_version_and_migration_registry(tmp_path: Path) -> None:
    service = ProjectService()
    root = tmp_path / "schema"
    identity, database = service.create_project(root, "Schema Test")

    assert database.get_meta("schema_version") == "2"
    row = database.execute(
        "SELECT version, name FROM migration_registry WHERE version = 1"
    ).fetchone()
    assert row is not None
    assert row["name"] == "001_initial_project_schema"
    foundation_row = database.execute(
        "SELECT version, name FROM migration_registry WHERE version = 2"
    ).fetchone()
    assert foundation_row is not None
    assert foundation_row["name"] == "002_settings_and_canon_foundation"
    service.close_project()


def test_backup_verifies_and_restore_preserves_original(tmp_path: Path) -> None:
    root = tmp_path / "original"
    service = ProjectService()
    identity, database = service.create_project(root, "Backup Test")
    database.set_meta("marker", "preserved")
    archive = service.create_backup(root)

    assert archive.is_file()
    assert archive.suffix == ".zip"

    destination = tmp_path / "restored"
    restored_identity, restored_database = service.restore_backup(archive, destination)
    assert restored_identity.book_id == identity.book_id
    assert restored_database.get_meta("marker") == "preserved"
    assert restored_database.verify_integrity() == "ok"
    assert (root / "project.sqlite").is_file()
    service.close_project()


def test_corrupt_backup_is_rejected(tmp_path: Path) -> None:
    root = tmp_path / "original"
    service = ProjectService()
    service.create_project(root, "Corruption Test")
    archive = service.create_backup(root)
    corrupted = tmp_path / "corrupted.zip"
    with zipfile.ZipFile(archive, "r") as source:
        project_json = bytearray(source.read("project.json"))
        project_json[-3] ^= 0xFF
        entries = {
            name: source.read(name)
            for name in source.namelist()
            if name != "project.json"
        }
    with zipfile.ZipFile(corrupted, "w", zipfile.ZIP_DEFLATED) as destination:
        destination.writestr("project.json", project_json)
        for name, content in entries.items():
            destination.writestr(name, content)

    with pytest.raises(ValueError, match="project manifest hash mismatch"):
        service.restore_backup(corrupted, tmp_path / "restored")
