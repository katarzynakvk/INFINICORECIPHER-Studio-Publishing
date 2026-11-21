from pathlib import Path

from backend.api.app import create_app


def test_settings_and_canon_api(tmp_path: Path) -> None:
    library = tmp_path / "library"
    app = create_app(library)
    client = app.test_client()

    created = client.post("/api/v1/projects", json={"title": "Canon Test"})
    assert created.status_code == 201
    root = created.get_json()["data"]["project"]["root"]
    opened = client.post("/api/v1/projects/open", json={"root": root})
    assert opened.status_code == 200

    unset = client.get(
        "/api/v1/settings",
        query_string={"scope": "BOOK", "scope_id": "book-1", "key": "trim_size"},
    )
    assert unset.status_code == 200
    assert unset.get_json()["data"]["state"] == "UNSET"

    setting = client.post(
        "/api/v1/settings",
        json={
            "scope": "BOOK",
            "scope_id": "book-1",
            "key": "trim_size",
            "value": "6x9",
        },
    )
    assert setting.status_code == 200
    assert setting.get_json()["data"]["revision"] == 1

    canon = client.post(
        "/api/v1/canon",
        json={
            "canon_id": "character:mira",
            "payload": {"hair": "black"},
            "locks": ["LOCK_CHARACTER"],
        },
    )
    assert canon.status_code == 201

    approved = client.post(
        "/api/v1/canon/approve",
        json={"canon_id": "character:mira", "revision": 1, "actor_id": "founder"},
    )
    assert approved.status_code == 200
    assert approved.get_json()["data"]["state"] == "APPROVED"

    locked = client.post(
        "/api/v1/canon/lock",
        json={"canon_id": "character:mira", "revision": 1},
    )
    assert locked.status_code == 200
    assert locked.get_json()["data"]["state"] == "LOCKED"

    stale = client.post(
        "/api/v1/canon/update",
        json={
            "canon_id": "character:mira",
            "payload": {"hair": "red"},
            "expected_revision": 1,
        },
    )
    assert stale.status_code == 409
    assert stale.get_json()["error"]["code"] == "CANON_LOCKED"
