from pathlib import Path

from backend.api.app import create_app


def test_project_api_create_list_open_close(tmp_path: Path) -> None:
    library = tmp_path / "library"
    app = create_app(library)
    client = app.test_client()

    health = client.get("/api/v1/health")
    assert health.status_code == 200
    assert health.get_json()["data"]["status"] == "AVAILABLE"

    created = client.post("/api/v1/projects", json={"title": "Rules For Loving Me"})
    assert created.status_code == 201
    envelope = created.get_json()
    assert envelope["success"] is True
    book_id = envelope["data"]["project"]["book_id"]

    listed = client.get("/api/v1/projects")
    assert listed.status_code == 200
    assert listed.get_json()["data"]["projects"][0]["book_id"] == book_id

    project = listed.get_json()["data"]["projects"][0]
    opened = client.post("/api/v1/projects/open", json={"root": project["root"]})
    assert opened.status_code == 200

    closed = client.post("/api/v1/projects/close")
    assert closed.status_code == 200
    assert closed.get_json()["data"]["closed"] is True


def test_project_api_blocks_path_traversal(tmp_path: Path) -> None:
    library = tmp_path / "library"
    app = create_app(library)
    client = app.test_client()

    response = client.post(
        "/api/v1/projects",
        json={"title": "Unsafe", "folder_name": "../outside"},
    )
    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "PATH_TRAVERSAL_BLOCKED"
