from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal


@dataclass(frozen=True)
class ProjectIdentity:
    book_id: str
    title: str
    schema_version: int
    created_at: str
    state: Literal["ACTIVE", "ARCHIVED"] = "ACTIVE"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
