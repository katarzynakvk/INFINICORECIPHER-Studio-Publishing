from pathlib import Path
from threading import Lock
from typing import Any

from flask import Flask, g, jsonify, request

from backend.services.project_service import ProjectService
from backend.services.settings_service import SettingsService
from backend.services.canon_service import CanonLocked, CanonService, RevisionConflict


def success(data: Any, status: int = 200):
    return jsonify({"success": True, "data": data, "error": None}), status


def error(code: str, message: str, status: int):
    return jsonify(
        {
            "success": False,
            "data": None,
            "error": {"code": code, "message": message},
        }
    ), status


def create_app(projects_root: Path, service: ProjectService | None = None) -> Flask:
    app = Flask(__name__)
    projects_root = projects_root.resolve()
    projects_root.mkdir(parents=True, exist_ok=True)
    project_service = service or ProjectService()
    settings_service = SettingsService()
    canon_service = CanonService()
    request_lock = Lock()

    @app.before_request
    def serialize_project_requests():
        request_lock.acquire()
        g.project_request_locked = True

    @app.teardown_request
    def release_project_request(_error):
        if g.pop("project_request_locked", False):
            request_lock.release()

    def project_payload(identity: Any, root: Path) -> dict[str, Any]:
        return {
            "book_id": identity.book_id,
            "title": identity.title,
            "schema_version": identity.schema_version,
            "created_at": identity.created_at,
            "state": identity.state,
            "root": str(root),
        }

    @app.get("/api/v1/health")
    def health():
        return success({"status": "AVAILABLE", "project_open": project_service.open_project_root is not None})

    @app.get("/api/v1/projects")
    def list_projects():
        projects = []
        for root in sorted(projects_root.iterdir(), key=lambda item: item.name.lower()):
            if not root.is_dir():
                continue
            try:
                identity = project_service.repository.read(root)
            except (FileNotFoundError, KeyError, ValueError, OSError):
                continue
            projects.append(project_payload(identity, root))
        return success({"projects": projects})

    @app.post("/api/v1/projects")
    def create_project():
        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            return error("INVALID_REQUEST", "JSON object required", 400)
        title = body.get("title")
        if not isinstance(title, str) or not title.strip():
            return error("INVALID_REQUEST", "title is required", 400)
        folder_name = body.get("folder_name")
        if folder_name is not None:
            if not isinstance(folder_name, str) or folder_name in ("", ".", ".."):
                return error("INVALID_REQUEST", "folder_name is invalid", 400)
            candidate = (projects_root / folder_name).resolve()
            if candidate.parent != projects_root:
                return error("PATH_TRAVERSAL_BLOCKED", "Project path is outside the project library", 400)
        else:
            slug = "".join(
                character.lower() if character.isalnum() else "-"
                for character in title.strip()
            ).strip("-")
            candidate = projects_root / (slug or "untitled-book")
        try:
            identity, _ = project_service.create_project(candidate, title.strip())
        except FileExistsError as exc:
            return error("PROJECT_EXISTS", str(exc), 409)
        except OSError as exc:
            return error("STORAGE_ERROR", str(exc), 500)
        return success({"project": project_payload(identity, candidate)}, 201)

    @app.post("/api/v1/projects/open")
    def open_project():
        body = request.get_json(silent=True)
        if not isinstance(body, dict) or not isinstance(body.get("root"), str):
            return error("INVALID_REQUEST", "root is required", 400)
        root = Path(body["root"]).resolve()
        if root.parent != projects_root:
            return error("PATH_TRAVERSAL_BLOCKED", "Project path is outside the project library", 400)
        try:
            identity, _ = project_service.open_project(root)
        except FileNotFoundError:
            return error("NOT_FOUND", "Project manifest not found", 404)
        except (ValueError, RuntimeError) as exc:
            return error("INVALID_PROJECT", str(exc), 409)
        return success({"project": project_payload(identity, root)})

    @app.post("/api/v1/projects/close")
    def close_project():
        project_service.close_project()
        return success({"closed": True})

    @app.post("/api/v1/projects/rename")
    def rename_project():
        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            return error("INVALID_REQUEST", "JSON object required", 400)
        root_value = body.get("root")
        title = body.get("title")
        book_id = body.get("book_id")
        if not isinstance(root_value, str) or not isinstance(title, str) or not title.strip():
            return error("INVALID_REQUEST", "root and title are required", 400)
        root = Path(root_value).resolve()
        if root.parent != projects_root:
            return error("PATH_TRAVERSAL_BLOCKED", "Project path is outside the project library", 400)
        try:
            current = project_service.repository.read(root)
            if current.book_id != book_id:
                return error("REVISION_CONFLICT", "Project identity does not match", 409)
            updated = project_service.rename_project(root, title.strip(), current)
        except FileNotFoundError:
            return error("NOT_FOUND", "Project manifest not found", 404)
        return success({"project": project_payload(updated, root)})

    @app.post("/api/v1/projects/backup")
    def backup_project():
        body = request.get_json(silent=True)
        if not isinstance(body, dict) or not isinstance(body.get("root"), str):
            return error("INVALID_REQUEST", "root is required", 400)
        root = Path(body["root"]).resolve()
        if root.parent != projects_root:
            return error("PATH_TRAVERSAL_BLOCKED", "Project path is outside the project library", 400)
        try:
            archive = project_service.create_backup(root)
        except (FileNotFoundError, ValueError, RuntimeError) as exc:
            return error("BACKUP_FAILED", str(exc), 409)
        except OSError as exc:
            return error("STORAGE_ERROR", str(exc), 500)
        return success({"archive": str(archive), "state": "BACKUP_VERIFIED"})

    def require_open_database():
        database = project_service._database
        if database is None:
            raise LookupError("No project is open")
        return database

    @app.post("/api/v1/settings")
    def set_setting():
        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            return error("INVALID_REQUEST", "JSON object required", 400)
        scope = body.get("scope")
        scope_id = body.get("scope_id")
        key = body.get("key")
        if scope not in {
            "APPLICATION", "PROJECT", "BOOK", "EDITION", "RUNTIME",
            "AI_PROVIDER", "STORAGE", "SECURITY_CREDENTIAL_REFERENCE",
        } or not isinstance(scope_id, str) or not isinstance(key, str):
            return error("INVALID_REQUEST", "Valid scope, scope_id and key are required", 400)
        if "value" not in body:
            return error("INVALID_REQUEST", "value is required", 400)
        try:
            database = require_open_database()
            setting = settings_service.set_setting(
                database, scope, scope_id, key, body["value"]
            )
        except LookupError as exc:
            return error("NOT_FOUND", str(exc), 409)
        return success({
            "setting_id": setting.setting_id,
            "scope": setting.scope,
            "scope_id": setting.scope_id,
            "key": setting.key,
            "value": setting.value,
            "state": setting.state,
            "revision": setting.revision,
        })

    @app.get("/api/v1/settings")
    def get_setting():
        scope = request.args.get("scope")
        scope_id = request.args.get("scope_id")
        key = request.args.get("key")
        try:
            database = require_open_database()
            setting = settings_service.get_setting(database, scope, scope_id, key)
        except LookupError as exc:
            return error("NOT_FOUND", str(exc), 409)
        if setting is None:
            return success({"setting": None, "state": "UNSET"})
        return success({
            "setting": {
                "setting_id": setting.setting_id,
                "scope": setting.scope,
                "scope_id": setting.scope_id,
                "key": setting.key,
                "value": setting.value,
                "state": setting.state,
                "revision": setting.revision,
            }
        })

    @app.post("/api/v1/canon")
    def create_canon():
        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            return error("INVALID_REQUEST", "JSON object required", 400)
        canon_id = body.get("canon_id")
        payload = body.get("payload")
        if not isinstance(canon_id, str) or not isinstance(payload, dict):
            return error("INVALID_REQUEST", "canon_id and payload are required", 400)
        locks = tuple(body.get("locks", []))
        try:
            database = require_open_database()
            revision = canon_service.create(database, canon_id, payload, locks)
        except LookupError as exc:
            return error("NOT_FOUND", str(exc), 409)
        except RevisionConflict as exc:
            return error("REVISION_CONFLICT", str(exc), 409)
        return success(canon_payload(revision), 201)

    @app.post("/api/v1/canon/update")
    def update_canon():
        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            return error("INVALID_REQUEST", "JSON object required", 400)
        canon_id = body.get("canon_id")
        payload = body.get("payload")
        expected = body.get("expected_revision")
        if not isinstance(canon_id, str) or not isinstance(payload, dict) or not isinstance(expected, int):
            return error("INVALID_REQUEST", "canon_id, payload and expected_revision are required", 400)
        try:
            database = require_open_database()
            revision = canon_service.update(database, canon_id, expected, payload)
        except LookupError as exc:
            return error("NOT_FOUND", str(exc), 409)
        except RevisionConflict as exc:
            return error("REVISION_CONFLICT", str(exc), 409)
        except CanonLocked as exc:
            return error("CANON_LOCKED", str(exc), 409)
        return success(canon_payload(revision))

    @app.post("/api/v1/canon/approve")
    def approve_canon():
        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            return error("INVALID_REQUEST", "JSON object required", 400)
        canon_id = body.get("canon_id")
        revision = body.get("revision")
        actor_id = body.get("actor_id")
        if not isinstance(canon_id, str) or not isinstance(revision, int) or not isinstance(actor_id, str):
            return error("INVALID_REQUEST", "canon_id, revision and actor_id are required", 400)
        try:
            database = require_open_database()
            approved = canon_service.approve(database, canon_id, revision, actor_id)
        except LookupError as exc:
            return error("NOT_FOUND", str(exc), 409)
        except RevisionConflict as exc:
            return error("REVISION_CONFLICT", str(exc), 409)
        return success(canon_payload(approved))

    @app.post("/api/v1/canon/lock")
    def lock_canon():
        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            return error("INVALID_REQUEST", "JSON object required", 400)
        canon_id = body.get("canon_id")
        revision = body.get("revision")
        if not isinstance(canon_id, str) or not isinstance(revision, int):
            return error("INVALID_REQUEST", "canon_id and revision are required", 400)
        try:
            database = require_open_database()
            locked = canon_service.lock(database, canon_id, revision)
        except LookupError as exc:
            return error("NOT_FOUND", str(exc), 409)
        except RevisionConflict as exc:
            return error("REVISION_CONFLICT", str(exc), 409)
        except CanonLocked as exc:
            return error("CANON_LOCKED", str(exc), 409)
        return success(canon_payload(locked))

    def canon_payload(revision):
        return {
            "canon_id": revision.canon_id,
            "revision": revision.revision,
            "parent_revision": revision.parent_revision,
            "state": revision.state,
            "payload": revision.payload,
            "locks": list(revision.locks),
        }

    return app
