from dataclasses import dataclass
from pathlib import PurePath
from uuid import uuid4


SUPPORTED_EXTENSIONS = {
    ".md": "markdown",
    ".markdown": "markdown",
    ".txt": "text",
    ".docx": "docx",
    ".pdf": "pdf",
    ".html": "html",
    ".htm": "html",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".webp": "image",
}


@dataclass(frozen=True)
class UploadedFileRecord:
    file_id: str
    filename: str
    size_bytes: int
    extension: str
    detected_type: str
    supported: bool


class FileRegistry:
    def __init__(self) -> None:
        self._records: dict[str, UploadedFileRecord] = {}

    def add(self, filename: str, content: bytes) -> UploadedFileRecord:
        extension = detect_extension(filename)
        detected_type = detect_document_type(filename)
        record = UploadedFileRecord(
            file_id=str(uuid4()),
            filename=PurePath(filename).name or "upload",
            size_bytes=len(content),
            extension=extension,
            detected_type=detected_type,
            supported=detected_type != "unknown",
        )
        self._records[record.file_id] = record
        return record

    def get(self, file_id: str) -> UploadedFileRecord | None:
        return self._records.get(file_id)


def detect_extension(filename: str) -> str:
    return PurePath(filename).suffix.lower()


def detect_document_type(filename: str) -> str:
    extension = detect_extension(filename)
    return SUPPORTED_EXTENSIONS.get(extension, "unknown")


file_registry = FileRegistry()
