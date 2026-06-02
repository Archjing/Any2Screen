#!/usr/bin/env python3
"""Markdown to long image converter."""
import argparse
import os
from pathlib import Path
import tempfile

from markdown_it import MarkdownIt
from playwright.sync_api import sync_playwright


CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC", "PingFang SC", "Microsoft YaHei", "Helvetica Neue", sans-serif;
    max-width: 900px;
    margin: 0 auto;
    padding: 48px 56px;
    background: #ffffff;
    color: #1a1a1a;
    line-height: 1.85;
    font-size: 15.5px;
    -webkit-font-smoothing: antialiased;
}
h1 { font-size: 28px; font-weight: 700; color: #111; border-bottom: 3px solid #2563eb; padding-bottom: 12px; margin: 0 0 28px 0; letter-spacing: -0.5px; }
h2 { font-size: 21px; font-weight: 600; color: #1e293b; border-left: 4px solid #2563eb; padding-left: 12px; margin: 36px 0 16px 0; }
h3 { font-size: 17px; font-weight: 600; color: #334155; margin: 24px 0 10px 0; }

table {
    width: 100%;
    border-collapse: collapse;
    margin: 18px 0;
    font-size: 14.5px;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    overflow: hidden;
}
thead { background: #f1f5f9; }
th {
    padding: 10px 14px;
    text-align: left;
    font-weight: 600;
    color: #1e293b;
    border-right: 1px solid #e2e8f0;
    border-bottom: 2px solid #cbd5e1;
    white-space: nowrap;
}
td {
    padding: 9px 14px;
    border-right: 1px solid #e2e8f0;
    border-bottom: 1px solid #e5e7eb;
    vertical-align: top;
}
tr:last-child td { border-bottom: none; }
td:last-child, th:last-child { border-right: none; }
tbody tr:nth-child(even) { background: #f8fafc; }
tbody tr:hover { background: #eff6ff; }

blockquote {
    border-left: 4px solid #f59e0b;
    margin: 18px 0;
    padding: 12px 20px;
    background: #fffbeb;
    color: #78350f;
    border-radius: 0 6px 6px 0;
}
blockquote p { margin: 4px 0; }
code { background: #f1f5f9; padding: 2px 7px; border-radius: 4px; font-size: 87%; color: #e11d48; font-family: "JetBrains Mono", "Fira Code", monospace; }
pre { background: #1e293b; color: #e2e8f0; padding: 16px 20px; border-radius: 8px; overflow-x: auto; margin: 16px 0; }
pre code { background: none; color: inherit; padding: 0; font-size: 13.5px; }
strong { color: #dc2626; font-weight: 600; }
hr { border: none; border-top: 1px solid #e5e7eb; margin: 28px 0; }
p { margin: 8px 0; }
ul, ol { margin: 10px 0; padding-left: 24px; }
li { margin: 4px 0; }
a { color: #2563eb; text-decoration: none; }
"""


def normalize_markdown_tables(md_text: str) -> str:
    """Trim accidental leading whitespace from markdown table rows."""
    fixed_lines = []
    for line in md_text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("|"):
            fixed_lines.append(stripped)
        else:
            fixed_lines.append(line)
    return "\n".join(fixed_lines)


def markdown_to_html(md_text: str) -> str:
    md = MarkdownIt("commonmark", {"breaks": True, "html": True})
    md.enable(["table", "strikethrough", "linkify"])
    html_body = md.render(normalize_markdown_tables(md_text))
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><style>{CSS}</style></head>
<body>
{html_body}
</body>
</html>"""


def resolve_output_path(input_path: Path, output: Path | None, image_format: str) -> Path:
    suffix = f".{image_format}"
    if output is None:
        return input_path.with_suffix(suffix)
    if output.suffix:
        return output
    return output / input_path.with_suffix(suffix).name


def convert(input_path: Path, output_path: Path, width: int, image_format: str) -> tuple[int, int, int]:
    md_text = input_path.read_text(encoding="utf-8")
    full_html = markdown_to_html(md_text)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8", delete=False) as tmp:
        tmp.write(full_html)
        html_path = Path(tmp.name)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": width, "height": 800})
            page.goto(f"file://{html_path}", wait_until="networkidle")

            height = page.evaluate("document.body.scrollHeight")
            page.set_viewport_size({"width": width, "height": height + 40})
            page.screenshot(path=str(output_path), full_page=True, type=image_format)
            browser.close()
    finally:
        html_path.unlink(missing_ok=True)

    size = os.path.getsize(output_path)
    return size, width, height + 40


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert Markdown to a long image")
    parser.add_argument("input", type=Path, help="Markdown file to convert")
    parser.add_argument("-o", "--output", type=Path, default=None,
                        help="Output image file or directory (default: input sibling)")
    parser.add_argument("--width", type=int, default=960,
                        help="Viewport/image width in pixels (default: 960)")
    parser.add_argument("--format", choices=("png", "jpeg"), default="png",
                        help="Output image format (default: png)")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"ERROR: not found: {args.input}")
        return 1
    if args.input.suffix.lower() not in (".md", ".markdown"):
        print(f"ERROR: not a markdown file: {args.input}")
        return 1
    if args.width < 320:
        print("ERROR: --width must be at least 320")
        return 1

    output_path = resolve_output_path(args.input, args.output, args.format)
    size, width, height = convert(args.input, output_path, args.width, args.format)
    print(f"Image: {output_path}")
    print(f"Size: {size} bytes ({size // 1024} KB)")
    print(f"Dimensions: {width} x {height} px")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
