import tempfile
from pathlib import Path
from urllib.parse import quote

from any2html import generate_html
from html2screen import render_image, render_pdf
from web.document_preview import build_preview_markdown
from web.files import UploadedFileRecord

SCREEN_WIDTHS = {"small": 430, "large": 1080}
IMAGE_FORMATS = {"png", "jpeg"}


def export_html(record: UploadedFileRecord) -> str:
    # 将上传记录转换为完整 HTML 导出内容。
    markdown = build_preview_markdown(record.detected_type, record.filename, record.content)
    return generate_html(markdown, Path(record.filename))


def export_html_path(record: UploadedFileRecord) -> Path:
    # 将 HTML 导出文件写入上传文件所在目录。
    output_path = record.path.with_suffix(".html")
    output_path.write_text(export_html(record), encoding="utf-8")
    return output_path


def export_pdf_path(record: UploadedFileRecord) -> Path:
    # 将 A4 PDF 导出文件写入上传文件所在目录。
    html = export_html(record)
    pdf_path = record.path.with_suffix(".pdf")
    with tempfile.TemporaryDirectory(prefix="any2screen-export-html-") as tmp:
        html_path = Path(tmp) / f"{Path(record.filename).stem or 'export'}.html"
        html_path.write_text(html, encoding="utf-8")
        if not render_pdf(html_path, pdf_path, verbose=False, wechat=False):
            raise RuntimeError("PDF export failed")
    return pdf_path


def export_wechat_pdf_path(record: UploadedFileRecord) -> Path:
    # 将微信阅读 PDF 导出文件写入上传文件所在目录。
    html = export_html(record)
    pdf_path = record.path.with_suffix(".wechat.pdf")
    with tempfile.TemporaryDirectory(prefix="any2screen-export-html-") as tmp:
        html_path = Path(tmp) / f"{Path(record.filename).stem or 'export'}.html"
        html_path.write_text(html, encoding="utf-8")
        if not render_pdf(html_path, pdf_path, verbose=False, wechat=True):
            raise RuntimeError("WeChat PDF export failed")
    return pdf_path


def export_image_path(record: UploadedFileRecord, screen: str, image_format: str) -> Path:
    # 按屏幕预设将上传记录导出为长图并写入上传文件所在目录。
    if screen not in SCREEN_WIDTHS:
        raise ValueError(f"unsupported screen preset: {screen}")
    if image_format not in IMAGE_FORMATS:
        raise ValueError(f"unsupported image format: {image_format}")

    html = export_html(record)
    image_path = record.path.with_name(f"{record.path.stem}.{screen}.{image_format}")
    with tempfile.TemporaryDirectory(prefix="any2screen-export-html-") as tmp:
        html_path = Path(tmp) / f"{Path(record.filename).stem or 'export'}.html"
        html_path.write_text(html, encoding="utf-8")
        ok, _, _, _ = render_image(
            html_path,
            image_path,
            width=SCREEN_WIDTHS[screen],
            image_format=image_format,
            verbose=False,
        )
        if not ok:
            raise RuntimeError("Image export failed")
    return image_path


def export_pdf(record: UploadedFileRecord) -> bytes:
    # 将上传记录转换为 A4 PDF 导出字节。
    return export_pdf_path(record).read_bytes()


def export_filename(filename: str, suffix: str) -> str:
    # 根据上传文件名生成安全的导出文件名。
    stem = Path(filename).stem or "export"
    return f"{stem}{suffix}"


def content_disposition(filename: str) -> str:
    # 生成同时兼容 ASCII 回退名和 UTF-8 文件名的下载响应头。
    fallback = "".join(_latin1_safe_char(char) for char in (filename or "export")) or "export"
    escaped_fallback = fallback.replace("\\", "\\\\").replace('"', '\\"')
    return f"attachment; filename=\"{escaped_fallback}\"; filename*=UTF-8''{quote(filename)}"


def _latin1_safe_char(char: str) -> str:
    try:
        char.encode("latin-1")
    except UnicodeEncodeError:
        return "_"
    return char
