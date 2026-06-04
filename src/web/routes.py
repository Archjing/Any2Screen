from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, File, HTTPException, Response, UploadFile

from preview import PreviewOptions, generate_preview_html
from web.document_preview import build_preview_markdown
from web.export import content_disposition, export_filename, export_html_path, export_image_path, export_pdf_path, export_wechat_pdf_path
from web.files import file_registry
from web.schemas import FileUploadResponse, HealthResponse, PreviewResponse, VersionResponse


router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    # 返回 API 健康状态和当前 UTC 时间。
    return HealthResponse(status="ok", timestamp=datetime.now(timezone.utc))


@router.get("/version", response_model=VersionResponse, tags=["system"])
def version() -> VersionResponse:
    # 返回服务版本和当前已开放的能力列表。
    return VersionResponse(
        name="any2screen",
        api_version="0.1.0",
        capabilities=["upload", "preview", "convert", "export"],
    )


@router.post("/files", response_model=FileUploadResponse, tags=["files"])
async def upload_file(file: UploadFile = File(...)) -> FileUploadResponse:
    # 接收单文件上传并返回格式识别后的文件元数据。
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
    # 根据 file_id 生成 Markdown/TXT/DOCX/PDF 的轻量 HTML 预览数据。
    record = file_registry.get(file_id)
    if record is None:
        raise HTTPException(status_code=404, detail="file not found")
    try:
        markdown = build_preview_markdown(record.detected_type, record.filename, record.content)
    except UnicodeDecodeError as e:
        raise HTTPException(status_code=400, detail="file must be UTF-8 encoded") from e
    except ValueError as e:
        raise HTTPException(status_code=415, detail="preview only supports Markdown, TXT, DOCX and PDF files") from e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"failed to build preview: {e}") from e

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
    # 返回可直接嵌入 iframe 的 HTML 预览响应。
    preview = preview_file(file_id, blocks=blocks, table_rows=table_rows, code_lines=code_lines)
    return Response(content=_with_root_base(preview.html), media_type="text/html; charset=utf-8")


@router.get("/exports/{file_id}/html", response_class=Response, tags=["exports"])
def export_html_file(file_id: str) -> Response:
    # 根据 file_id 生成完整 HTML 下载响应。
    record = _get_export_record(file_id)
    html_path = export_html_path(record)
    return Response(
        content=_with_root_base(html_path.read_text(encoding="utf-8")),
        media_type="text/html; charset=utf-8",
        headers={"Content-Disposition": content_disposition(export_filename(record.filename, ".html"))},
    )


@router.get("/exports/{file_id}/pdf", response_class=Response, tags=["exports"])
def export_pdf_file(file_id: str) -> Response:
    # 根据 file_id 生成 A4 PDF 下载响应。
    record = _get_export_record(file_id)
    pdf_path = export_pdf_path(record)
    return Response(
        content=pdf_path.read_bytes(),
        media_type="application/pdf",
        headers={"Content-Disposition": content_disposition(export_filename(record.filename, ".pdf"))},
    )


@router.get("/exports/{file_id}/wechat-pdf", response_class=Response, tags=["exports"])
def export_wechat_pdf_file(file_id: str) -> Response:
    # 根据 file_id 生成微信阅读 PDF 下载响应。
    record = _get_export_record(file_id)
    pdf_path = export_wechat_pdf_path(record)
    return Response(
        content=pdf_path.read_bytes(),
        media_type="application/pdf",
        headers={"Content-Disposition": content_disposition(export_filename(record.filename, ".wechat.pdf"))},
    )


@router.get("/exports/{file_id}/image", response_class=Response, tags=["exports"])
def export_image_file(
    file_id: str,
    screen: Literal["small", "large"] = "small",
    format: Literal["png", "jpeg"] = "png",
) -> Response:
    # 根据 file_id、屏幕预设和图片格式生成长图下载响应。
    record = _get_export_record(file_id)
    image_path = export_image_path(record, screen=screen, image_format=format)
    return Response(
        content=image_path.read_bytes(),
        media_type=f"image/{format}",
        headers={"Content-Disposition": content_disposition(export_filename(record.filename, f".{screen}.{format}"))},
    )


def _get_export_record(file_id: str):
    # 获取可导出的上传记录并转换错误为 HTTP 响应。
    record = file_registry.get(file_id)
    if record is None:
        raise HTTPException(status_code=404, detail="file not found")
    try:
        build_preview_markdown(record.detected_type, record.filename, record.content)
    except UnicodeDecodeError as e:
        raise HTTPException(status_code=400, detail="file must be UTF-8 encoded") from e
    except ValueError as e:
        raise HTTPException(status_code=415, detail="export only supports Markdown, TXT, DOCX and PDF files") from e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"failed to prepare export: {e}") from e
    return record


def _with_root_base(html: str) -> str:
    # 为预览 HTML 注入根路径 base，修正相对资源地址。
    if "<base " in html:
        return html
    return html.replace("<head>", '<head>\n<base href="/">', 1)
