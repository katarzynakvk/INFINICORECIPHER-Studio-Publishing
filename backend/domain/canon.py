from dataclasses import dataclass
from typing import Literal


CanonState = Literal["DRAFT", "REVIEW", "APPROVED", "LOCKED", "STALE"]
CanonLock = Literal[
    "LOCK_TEXT",
    "LOCK_CHARACTER",
    "LOCK_STYLE",
    "LOCK_LAYOUT",
    "LOCK_PAGE",
]


@dataclass(frozen=True)
class CanonRevision:
    canon_id: str
    revision: int
    parent_revision: int | None
    state: CanonState
    payload: dict
    locks: tuple[CanonLock, ...]
