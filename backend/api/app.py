from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request

from backend.services.project_service import ProjectService


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

    return app
