from datetime import datetime, timezone

from fastapi import APIRouter, File, UploadFile

from web.files import file_registry
from web.schemas import FileUploadResponse, HealthResponse, VersionResponse


router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    return HealthResponse(status="ok", timestamp=datetime.now(timezone.utc))


@router.get("/version", response_model=VersionResponse, tags=["system"])
def version() -> VersionResponse:
    return VersionResponse(
        name="any2screen",
        api_version="0.1.0",
        capabilities=["upload", "preview", "convert", "export"],
    )


@router.post("/files", response_model=FileUploadResponse, tags=["files"])
async def upload_file(file: UploadFile = File(...)) -> FileUploadResponse:
    content = await file.read()
    record = file_registry.add(file.filename or "upload", content)
    return FileUploadResponse(
        file_id=record.file_id,
        filename=record.filename,
        size_bytes=record.size_bytes,
        extension=record.extension,
        detected_type=record.detected_type,
        supported=record.supported,
    )
