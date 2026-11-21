import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


PROJECT_DIRECTORIES = (
    "sources/manuscripts",
    "sources/references",
    "sources/blueprints",
    "assets/illustrations",
    "assets/fonts",
    "assets/brand",
    "outputs/exports",
    "outputs/jobs",
    "outputs/staging",
    "outputs/artifacts",
    "backups",
    "temp",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    try:
        with os.fdopen(file_descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def initialize_project_directories(root: Path) -> None:
    for relative in PROJECT_DIRECTORIES:
        (root / relative).mkdir(parents=True, exist_ok=True)
