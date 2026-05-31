# md2html Pipeline

Batch Markdown -> Self-Contained HTML Converter

## Quick Start

```bash
pip install -r requirements.txt
python3 md2html.py input.md
```

## Features

- **Self-contained**: zero external CSS/JS/webfonts — one `.html` file, ready to open
- **Responsive**: three breakpoints (mobile <640px, tablet 640-1024px, desktop)
- **Dark mode**: auto-switch via `prefers-color-scheme`
- **Print-friendly**: dedicated `@media print` styles
- **GFM extended**: tables, strikethrough, task lists, footnotes, sub/superscript, definition lists
- **Batch mode**: process files, directories, or mixed inputs
- **Watch mode**: `--watch` to auto-rebuild on file changes

## Usage

```bash
# Single file (HTML only)
python3 md2html.py README.md

# Single file → HTML + PDF (ready for WeChat)
python3 md2html.py trip.md --wechat

# Whole directory
python3 md2html.py ~/notes/ -o ~/html_output/

# Whole directory → HTML + PDF
python3 md2html.py ~/notes/ -o ~/exports/ --pdf

# Multiple files and directories
python3 md2html.py doc1.md doc2.md ~/projects/ --wechat

# Write .html siblings next to .md files
python3 md2html.py --inplace *.md

# Watch for changes
python3 md2html.py --watch ~/notes/ -o ~/html/
```

### WeChat Sharing

Use `--wechat` (or `--pdf`) to generate PDFs alongside HTML.
PDFs can be sent via WeChat and opened inline with zoom and text selection.
Requires Playwright: `pip install playwright && playwright install chromium`

```bash
python3 md2html.py plan.md --wechat -o ~/exports/
# -> plan.html   (open in browser)
# -> plan.pdf    (send to WeChat, opens inline)
```

## Dependencies

- Python 3.8+
- [markdown-it-py](https://github.com/executablebooks/markdown-it-py)
- [mdit-py-plugins](https://github.com/executablebooks/mdit-py-plugins)
- [linkify-it-py](https://github.com/tsutsu3/linkify-it-py)
