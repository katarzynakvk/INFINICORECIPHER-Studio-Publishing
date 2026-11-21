from pathlib import Path
from threading import Event, Thread

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


def test_project_can_be_closed_from_another_request_thread(tmp_path: Path) -> None:
    app = create_app(tmp_path / "library")
    client = app.test_client()
    assert client.post("/api/v1/projects", json={"title": "First"}).status_code == 201
    results = []

    def close_project() -> None:
        with app.test_client() as other_client:
            response = other_client.post("/api/v1/projects/close")
            results.append((response.status_code, response.get_json()))

    thread = Thread(target=close_project)
    thread.start()
    thread.join(timeout=5)
    assert not thread.is_alive()
    assert results[0][0] == 200
    assert results[0][1]["data"]["closed"] is True
    assert client.get("/api/v1/health").get_json()["data"]["project_open"] is False


def test_project_requests_are_serialized(tmp_path: Path) -> None:
    app = create_app(tmp_path / "library")
    entered = Event()
    release = Event()
    second_entered = Event()

    @app.get("/test/block")
    def block():
        entered.set()
        release.wait(timeout=5)
        return "", 204

    @app.get("/test/second")
    def second():
        second_entered.set()
        return "", 204

    def get(path: str) -> None:
        with app.test_client() as client:
            client.get(path)

    first_thread = Thread(target=get, args=("/test/block",))
    second_thread = Thread(target=get, args=("/test/second",))
    first_thread.start()
    try:
        assert entered.wait(timeout=5)
        second_thread.start()
        assert not second_entered.wait(timeout=0.1)
    finally:
        release.set()
        first_thread.join(timeout=5)
        if second_thread.ident is not None:
            second_thread.join(timeout=5)
    assert not first_thread.is_alive()
    assert not second_thread.is_alive()
    assert second_entered.is_set()
