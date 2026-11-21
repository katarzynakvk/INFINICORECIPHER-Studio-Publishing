from typing import Generic, TypeVar

T = TypeVar("T")


class ApiError:
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
