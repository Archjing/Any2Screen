from dataclasses import dataclass
from pathlib import Path
import re

from any2html import generate_html


LIST_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")


@dataclass(frozen=True)
class PreviewOptions:
    max_blocks: int = 20
    max_table_rows: int = 20
    max_code_lines: int = 120


@dataclass(frozen=True)
class PreviewResult:
    markdown: str
    total_blocks: int
    included_blocks: int
    truncated: bool


@dataclass(frozen=True)
class _MarkdownBlock:
    lines: list[str]
    truncated: bool = False


def build_markdown_preview(md_text: str, options: PreviewOptions | None = None) -> PreviewResult:
    # 按语义块截断 Markdown 内容并返回轻量预览结果。
    """Return a lightweight Markdown preview by block count.

    This intentionally avoids PDF/browser rendering. It is the fast path for
    Web previews and only keeps the first N semantic Markdown blocks.
    """
    opts = options or PreviewOptions()
    if opts.max_blocks < 1:
        raise ValueError("max_blocks must be at least 1")
    if opts.max_table_rows < 1:
        raise ValueError("max_table_rows must be at least 1")
    if opts.max_code_lines < 1:
        raise ValueError("max_code_lines must be at least 1")

    blocks = _parse_markdown_blocks(md_text, opts)
    included = blocks[:opts.max_blocks]
    truncated = len(blocks) > len(included) or any(block.truncated for block in included)
    markdown = _join_blocks(included)
    return PreviewResult(
        markdown=markdown,
        total_blocks=len(blocks),
        included_blocks=len(included),
        truncated=truncated,
    )


def generate_preview_html(
    md_text: str,
    source_path: Path,
    options: PreviewOptions | None = None,
) -> tuple[str, PreviewResult]:
    # 生成轻量 Markdown 预览对应的完整 HTML 文档。
    result = build_markdown_preview(md_text, options)
    html = generate_html(result.markdown, source_path)
    return html, result


def _parse_markdown_blocks(md_text: str, options: PreviewOptions) -> list[_MarkdownBlock]:
    # 把 Markdown 文本切分成标题、段落、表格、代码块等预览块。
    lines = md_text.splitlines()
    blocks: list[_MarkdownBlock] = []
    i = 0

    while i < len(lines):
        if not lines[i].strip():
            i += 1
            continue

        if _is_fence_start(lines[i]):
            block, i = _consume_fenced_code(lines, i, options)
        elif _is_table_start(lines, i):
            block, i = _consume_table(lines, i, options)
        elif _is_single_line_block(lines[i]):
            block = _MarkdownBlock([lines[i]])
            i += 1
        elif LIST_RE.match(lines[i]):
            block, i = _consume_until_blank(lines, i)
        else:
            block, i = _consume_paragraph(lines, i)
        blocks.append(block)

    return blocks


def _is_fence_start(line: str) -> bool:
    # 判断当前行是否是围栏代码块的起始行。
    return bool(FENCE_RE.match(line))


def _is_table_start(lines: list[str], index: int) -> bool:
    # 判断当前位置是否是 Markdown 表格的起始行。
    return (
        index + 1 < len(lines)
        and "|" in lines[index]
        and _is_table_delimiter(lines[index + 1])
    )


def _is_table_delimiter(line: str) -> bool:
    # 判断当前行是否是 Markdown 表格分隔线。
    stripped = line.strip()
    return "|" in stripped and bool(stripped) and set(stripped) <= set("|-: ")


def _is_single_line_block(line: str) -> bool:
    # 判断当前行是否可作为独立单行块处理。
    stripped = line.strip()
    return (
        stripped.startswith("#")
        or stripped in {"---", "***", "___"}
        or stripped.startswith(">")
    )


def _consume_fenced_code(
    lines: list[str],
    start: int,
    options: PreviewOptions,
) -> tuple[_MarkdownBlock, int]:
    # 消费一个围栏代码块并按最大代码行数截断。
    first = lines[start]
    match = FENCE_RE.match(first)
    fence = match.group(1) if match else first.strip()[:3]
    fence_char = fence[0]
    min_len = len(fence)

    out = [first]
    code_lines = 0
    truncated = False
    i = start + 1

    while i < len(lines):
        line = lines[i]
        closing = line.strip().startswith(fence_char * min_len)
        if closing:
            out.append(line)
            i += 1
            break

        code_lines += 1
        if code_lines <= options.max_code_lines:
            out.append(line)
        else:
            truncated = True
        i += 1

    if i >= len(lines) and (not out or not out[-1].strip().startswith(fence_char * min_len)):
        out.append(fence_char * min_len)

    return _MarkdownBlock(out, truncated), i


def _consume_table(
    lines: list[str],
    start: int,
    options: PreviewOptions,
) -> tuple[_MarkdownBlock, int]:
    # 消费一个 Markdown 表格并按最大数据行数截断。
    table_lines = []
    i = start
    while i < len(lines) and lines[i].strip() and "|" in lines[i]:
        table_lines.append(lines[i])
        i += 1

    header = table_lines[:2]
    body = table_lines[2:]
    kept_body = body[:options.max_table_rows]
    truncated = len(body) > len(kept_body)
    return _MarkdownBlock(header + kept_body, truncated), i


def _consume_until_blank(lines: list[str], start: int) -> tuple[_MarkdownBlock, int]:
    # 从当前位置持续消费到空行作为一个块。
    out = []
    i = start
    while i < len(lines) and lines[i].strip():
        out.append(lines[i])
        i += 1
    return _MarkdownBlock(out), i


def _consume_paragraph(lines: list[str], start: int) -> tuple[_MarkdownBlock, int]:
    # 从当前位置消费普通段落直到遇到新块或空行。
    out = []
    i = start
    while i < len(lines):
        if not lines[i].strip():
            break
        if i > start and (_is_fence_start(lines[i]) or _is_table_start(lines, i) or _is_single_line_block(lines[i])):
            break
        out.append(lines[i])
        i += 1
    return _MarkdownBlock(out), i


def _join_blocks(blocks: list[_MarkdownBlock]) -> str:
    # 将预览块重新拼接成 Markdown 文本。
    chunks = ["\n".join(block.lines).rstrip() for block in blocks if block.lines]
    return "\n\n".join(chunk for chunk in chunks if chunk).rstrip() + "\n"
