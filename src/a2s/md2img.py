#!/usr/bin/env python3
"""Markdown to long image converter - handles tables, code blocks, Chinese text."""
import sys, os
from markdown_it import MarkdownIt
from playwright.sync_api import sync_playwright

INPUT = os.path.expanduser("~/workspace/KMS/My_logseq/pages/us-cn-stock-correlation-mapping.md")
OUTPUT = os.path.expanduser("~/workspace/KMS/library/reports/us-cn-stock-correlation-mapping.png")

# Read markdown
with open(INPUT) as f:
    md_text = f.read()

# Strip leading whitespace from table rows (fix for pandoc/markdown-it compatibility)
lines = md_text.split('\n')
fixed_lines = []
for line in lines:
    stripped = line.strip()
    if stripped.startswith('|') and stripped.endswith('|'):
        # This looks like a table row - preserve structure but trim leading spaces
        fixed_lines.append(stripped)
    elif stripped.startswith('|'):
        fixed_lines.append(stripped)
    else:
        fixed_lines.append(line)
md_text = '\n'.join(fixed_lines)

# Convert to HTML using markdown-it-py  
md = MarkdownIt('commonmark', {'breaks': True, 'html': True})
md.enable(['table', 'strikethrough', 'linkify'])
html_body = md.render(md_text)

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

/* === TABLES: the critical part === */
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

full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><style>{CSS}</style></head>
<body>
{html_body}
</body>
</html>"""

html_path = "/tmp/md2img_output.html"
with open(html_path, 'w') as f:
    f.write(full_html)

print(f"HTML: {len(full_html)} bytes")

# Screenshot with playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 960, "height": 800})
    page.goto(f"file://{html_path}", wait_until="networkidle")
    
    height = page.evaluate("document.body.scrollHeight")
    page.set_viewport_size({"width": 960, "height": height + 40})
    
    page.screenshot(path=OUTPUT, full_page=True)
    browser.close()

size = os.path.getsize(OUTPUT)
print(f"Image: {OUTPUT}")
print(f"Size: {size} bytes ({size//1024} KB)")
print(f"Dimensions: 960 x {height+40} px")
