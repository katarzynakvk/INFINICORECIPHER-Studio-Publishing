from dataclasses import dataclass
from typing import Literal


SettingScope = Literal[
    "APPLICATION",
    "PROJECT",
    "BOOK",
    "EDITION",
    "RUNTIME",
    "AI_PROVIDER",
    "STORAGE",
    "SECURITY_CREDENTIAL_REFERENCE",
]
SettingState = Literal["UNSET", "EXPLICIT", "DEFAULT"]


@dataclass(frozen=True)
class Setting:
    setting_id: str
    scope: SettingScope
    scope_id: str
    key: str
    value: object | None
    state: SettingState
    revision: int = 1
