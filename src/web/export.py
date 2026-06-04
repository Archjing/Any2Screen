import tempfile
from pathlib import Path

from any2html import generate_html
from html2screen import render_pdf
from web.document_preview import build_preview_markdown
from web.files import UploadedFileRecord


def export_html(record: UploadedFileRecord) -> str:
    # 将上传记录转换为完整 HTML 导出内容。
    markdown = build_preview_markdown(record.detected_type, record.filename, record.content)
    return generate_html(markdown, Path(record.filename))


def export_pdf(record: UploadedFileRecord) -> bytes:
    # 将上传记录转换为 A4 PDF 导出字节。
    html = export_html(record)
    with tempfile.TemporaryDirectory(prefix="any2screen-export-") as tmp:
        html_path = Path(tmp) / f"{Path(record.filename).stem or 'export'}.html"
        pdf_path = html_path.with_suffix(".pdf")
        html_path.write_text(html, encoding="utf-8")
        if not render_pdf(html_path, pdf_path, verbose=False, wechat=False):
            raise RuntimeError("PDF export failed")
        return pdf_path.read_bytes()


def export_filename(filename: str, suffix: str) -> str:
    # 根据上传文件名生成安全的导出文件名。
    stem = Path(filename).stem or "export"
    return f"{stem}{suffix}"
