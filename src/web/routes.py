from datetime import datetime, timezone

from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Response, UploadFile

from preview import PreviewOptions, generate_preview_html
from web.files import file_registry
from web.schemas import FileUploadResponse, HealthResponse, PreviewResponse, VersionResponse


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


@router.get("/previews/{file_id}", response_model=PreviewResponse, tags=["previews"])
def preview_file(
    file_id: str,
    blocks: int = 20,
    table_rows: int = 20,
    code_lines: int = 120,
) -> PreviewResponse:
    record = file_registry.get(file_id)
    if record is None:
        raise HTTPException(status_code=404, detail="file not found")
    if record.detected_type not in {"markdown", "text"}:
        raise HTTPException(status_code=415, detail="preview only supports Markdown and TXT files")

    try:
        text = record.content.decode("utf-8")
    except UnicodeDecodeError as e:
        raise HTTPException(status_code=400, detail="file must be UTF-8 encoded") from e

    markdown = text if record.detected_type == "markdown" else _text_to_markdown(text, record.filename)
    html, result = generate_preview_html(
        markdown,
        Path(record.filename),
        PreviewOptions(max_blocks=blocks, max_table_rows=table_rows, max_code_lines=code_lines),
    )
    return PreviewResponse(
        file_id=record.file_id,
        filename=record.filename,
        detected_type=record.detected_type,
        html=html,
        total_blocks=result.total_blocks,
        included_blocks=result.included_blocks,
        truncated=result.truncated,
    )


@router.get("/previews/{file_id}/html", response_class=Response, tags=["previews"])
def preview_html(
    file_id: str,
    blocks: int = 20,
    table_rows: int = 20,
    code_lines: int = 120,
) -> Response:
    preview = preview_file(file_id, blocks=blocks, table_rows=table_rows, code_lines=code_lines)
    return Response(content=preview.html, media_type="text/html; charset=utf-8")


def _text_to_markdown(text: str, filename: str) -> str:
    title = Path(filename).stem or "Preview"
    return f"# {title}\n\n```text\n{text.rstrip()}\n```\n"
