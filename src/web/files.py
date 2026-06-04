from dataclasses import dataclass
import json
import os
from pathlib import Path
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
    path: Path


class FileRegistry:
    def __init__(self, upload_root: Path | str = "data/uploads") -> None:
        # 初始化内存文件记录表。
        self._records: dict[str, UploadedFileRecord] = {}
        self.upload_root = Path(upload_root)

    def add(self, filename: str, content: bytes) -> UploadedFileRecord:
        # 保存上传文件内容和识别后的元数据。
        file_id = str(uuid4())
        safe_filename = PurePath(filename).name or "upload"
        path = self.upload_root / file_id / safe_filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        extension = detect_extension(filename)
        detected_type = detect_document_type(filename)
        record = UploadedFileRecord(
            file_id=file_id,
            filename=safe_filename,
            size_bytes=len(content),
            extension=extension,
            detected_type=detected_type,
            supported=detected_type != "unknown",
            content=content,
            path=path,
        )
        self._write_metadata(record)
        self._records[record.file_id] = record
        return record

    def get(self, file_id: str) -> UploadedFileRecord | None:
        # 根据 file_id 查找已上传文件记录。
        record = self._records.get(file_id)
        if record is not None:
            return record
        record = self._read_metadata(file_id)
        if record is not None:
            self._records[file_id] = record
        return record

    def _write_metadata(self, record: UploadedFileRecord) -> None:
        # 将上传记录元数据写入磁盘，支持跨进程恢复 file_id。
        metadata_path = record.path.parent / "record.json"
        metadata = {
            "file_id": record.file_id,
            "filename": record.filename,
            "size_bytes": record.size_bytes,
            "extension": record.extension,
            "detected_type": record.detected_type,
            "supported": record.supported,
            "path": record.path.name,
        }
        metadata_path.write_text(json.dumps(metadata, ensure_ascii=True), encoding="utf-8")

    def _read_metadata(self, file_id: str) -> UploadedFileRecord | None:
        # 从磁盘恢复上传记录，避免仅靠进程内内存导致 file_id 失效。
        metadata_path = self.upload_root / file_id / "record.json"
        if not metadata_path.exists():
            return None
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        path = metadata_path.parent / metadata["path"]
        if not path.exists():
            return None
        content = path.read_bytes()
        return UploadedFileRecord(
            file_id=metadata["file_id"],
            filename=metadata["filename"],
            size_bytes=metadata["size_bytes"],
            extension=metadata["extension"],
            detected_type=metadata["detected_type"],
            supported=metadata["supported"],
            content=content,
            path=path,
        )


def detect_extension(filename: str) -> str:
    # 提取文件名的小写扩展名用于后续格式识别。
    return PurePath(filename).suffix.lower()


def detect_document_type(filename: str) -> str:
    # 根据文件扩展名识别上传文档的类型。
    extension = detect_extension(filename)
    return SUPPORTED_EXTENSIONS.get(extension, "unknown")


file_registry = FileRegistry(os.environ.get("ANY2SCREEN_UPLOAD_ROOT", "data/uploads"))
