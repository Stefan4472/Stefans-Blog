from enum import Enum


class FileFiletype(str, Enum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    DOCUMENT = "DOCUMENT"

    def __str__(self) -> str:
        return str(self.value)
