from io import BytesIO
from pathlib import Path


def build_preview_markdown(detected_type: str, filename: str, content: bytes) -> str:
    # 根据上传文件类型把内容转换为可预览的 Markdown 文本。
    if detected_type == "markdown":
        return content.decode("utf-8")
    if detected_type == "text":
        return _text_to_markdown(content.decode("utf-8"), filename)
    if detected_type == "docx":
        return _docx_to_markdown(content, filename)
    if detected_type == "pdf":
        return _pdf_to_markdown(content, filename)
    raise ValueError(f"unsupported preview type: {detected_type}")


def _text_to_markdown(text: str, filename: str) -> str:
    # 将纯文本包装成带标题和代码块的 Markdown。
    title = Path(filename).stem or "Preview"
    return f"# {title}\n\n```text\n{text.rstrip()}\n```\n"


def _docx_to_markdown(content: bytes, filename: str) -> str:
    # 从 DOCX 字节内容中提取段落并转换成 Markdown。
    try:
        from docx import Document
    except ImportError as e:
        raise RuntimeError("DOCX preview requires python-docx") from e

    document = Document(BytesIO(content))
    lines = []
    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if not text:
            lines.append("")
            continue
        style = paragraph.style.name if paragraph.style else ""
        if "Heading 1" in style or "标题 1" in style:
            lines.append(f"# {text}")
        elif "Heading 2" in style or "标题 2" in style:
            lines.append(f"## {text}")
        elif "Heading 3" in style or "标题 3" in style:
            lines.append(f"### {text}")
        elif "Heading" in style or "标题" in style:
            lines.append(f"**{text}**")
        else:
            lines.append(text)

    markdown = "\n\n".join(lines).strip()
    if markdown:
        return markdown + "\n"
    return f"# {Path(filename).stem or 'Preview'}\n\n"


def _pdf_to_markdown(content: bytes, filename: str) -> str:
    # 从 PDF 字节内容中提取页面文本并转换成 Markdown。
    try:
        import PyPDF2
    except ImportError as e:
        raise RuntimeError("PDF preview requires PyPDF2") from e

    reader = PyPDF2.PdfReader(BytesIO(content))
    pages = []
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text()
        if text and text.strip():
            pages.append(f"## Page {index}\n\n{text.strip()}")

    body = "\n\n".join(pages).strip()
    title = Path(filename).stem or "Preview"
    if body:
        return f"# {title}\n\n{body}\n"
    return f"# {title}\n\nNo extractable text found.\n"
