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
    content: bytes


class FileRegistry:
    def __init__(self) -> None:
        # 初始化内存文件记录表。
        self._records: dict[str, UploadedFileRecord] = {}

    def add(self, filename: str, content: bytes) -> UploadedFileRecord:
        # 保存上传文件内容和识别后的元数据。
        extension = detect_extension(filename)
        detected_type = detect_document_type(filename)
        record = UploadedFileRecord(
            file_id=str(uuid4()),
            filename=PurePath(filename).name or "upload",
            size_bytes=len(content),
            extension=extension,
            detected_type=detected_type,
            supported=detected_type != "unknown",
            content=content,
        )
        self._records[record.file_id] = record
        return record

    def get(self, file_id: str) -> UploadedFileRecord | None:
        # 根据 file_id 查找已上传文件记录。
        return self._records.get(file_id)


def detect_extension(filename: str) -> str:
    # 提取文件名的小写扩展名用于后续格式识别。
    return PurePath(filename).suffix.lower()


def detect_document_type(filename: str) -> str:
    # 根据文件扩展名识别上传文档的类型。
    extension = detect_extension(filename)
    return SUPPORTED_EXTENSIONS.get(extension, "unknown")


file_registry = FileRegistry()
