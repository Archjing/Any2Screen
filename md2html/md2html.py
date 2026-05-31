#!/usr/bin/env python3
"""
md2html — Batch Markdown -> Self-Contained HTML Converter

Reads one or more .md files and produces beautiful, responsive, self-contained
HTML files with embedded stylesheets. Zero external dependencies at render time.

Usage:
  # Convert a single file
  python3 md2html.py README.md

  # Convert all .md files in a directory, output to another directory
  python3 md2html.py ~/notes/ -o ~/html_output/

  # Convert specific files
  python3 md2html.py doc1.md doc2.md doc3.md

  # Overwrite original .md files with .html siblings
  python3 md2html.py --inplace ~/notes/*.md

  # Watch mode (re-build on file change)
  python3 md2html.py --watch ~/notes/

Requires: Python 3.8+, markdown-it-py
"""

import argparse
import re
import sys
import time
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

from markdown_it import MarkdownIt

# Optional plugin imports
try:
    from mdit_py_plugins.deflist import deflist_plugin
    HAS_DEFLIST = True
except ImportError:
    HAS_DEFLIST = False

try:
    from mdit_py_plugins.footnote import footnote_plugin
    HAS_FOOTNOTE = True
except ImportError:
    HAS_FOOTNOTE = False

try:
    from mdit_py_plugins.subscript import sub_plugin
    HAS_SUBSCRIPT = True
except ImportError:
    HAS_SUBSCRIPT = False

try:
    from mdit_py_plugins.superscript import superscript_plugin
    HAS_SUPERSCRIPT = True
except ImportError:
    HAS_SUPERSCRIPT = False

try:
    from mdit_py_plugins.tasklists import tasklists_plugin
    HAS_TASKLISTS = True
except ImportError:
    HAS_TASKLISTS = False


# ──────────────────────────────────────────────
# CSS (embedded — zero external deps)
# ──────────────────────────────────────────────
STYLE_CSS = """\
/* ===== Reset & Base ===== */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg: #fafaf9;
  --surface: #ffffff;
  --text: #1c1917;
  --text-secondary: #57534e;
  --border: #e7e5e4;
  --accent: #0d9488;
  --accent-light: #ccfbf1;
  --accent-text: #ffffff;
  --code-bg: #f5f5f4;
  --code-text: #292524;
  --hr-color: #e7e5e4;
  --blockquote-border: #0d9488;
  --blockquote-bg: #f0fdfa;
  --table-stripe: #f5f5f4;
  --table-hover: #ecfdf5;
  --heading-border: #e7e5e4;
  --kbd-bg: #f5f5f4;
  --kbd-border: #d6d3d1;
  --mark-bg: #fef3c7;
  --img-shadow: 0 2px 8px rgba(0,0,0,0.08);
  --link-color: #0d9488;
  --link-hover: #0f766e;
  --max-width: 820px;
  --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans SC", "PingFang SC", "Microsoft YaHei", system-ui, sans-serif;
  --font-mono: "SF Mono", "Fira Code", "JetBrains Mono", "Cascadia Code", Consolas, monospace;
  --radius: 8px;
  --shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #1c1917;
    --surface: #292524;
    --text: #e7e5e4;
    --text-secondary: #a8a29e;
    --border: #44403c;
    --accent: #14b8a6;
    --accent-light: #134e4a;
    --accent-text: #042f2e;
    --code-bg: #44403c;
    --code-text: #e7e5e4;
    --hr-color: #44403c;
    --blockquote-border: #14b8a6;
    --blockquote-bg: #171717;
    --table-stripe: #292524;
    --table-hover: #1c1917;
    --heading-border: #44403c;
    --kbd-bg: #44403c;
    --kbd-border: #57534e;
    --mark-bg: #713f12;
    --img-shadow: 0 2px 8px rgba(0,0,0,0.3);
    --link-color: #5eead4;
    --link-hover: #99f6e4;
  }
}

html {
  font-size: 16px;
  -webkit-text-size-adjust: 100%;
  text-size-adjust: 100%;
}

body {
  font-family: var(--font-family);
  color: var(--text);
  background: var(--bg);
  line-height: 1.75;
  padding: 2rem 1rem;
  min-height: 100vh;
}

/* ===== Container ===== */
.container {
  max-width: var(--max-width);
  margin: 0 auto;
  background: var(--surface);
  border-radius: var(--radius);
  padding: 2rem 1.5rem;
  box-shadow: var(--shadow);
}

/* ===== Typography ===== */
h1, h2, h3, h4, h5, h6 {
  line-height: 1.3;
  font-weight: 600;
  color: var(--text);
  margin-top: 1.8em;
  margin-bottom: 0.5em;
  letter-spacing: -0.01em;
}

h1 { font-size: 2em; border-bottom: 2px solid var(--heading-border); padding-bottom: 0.3em; }
h2 { font-size: 1.5em; border-bottom: 1px solid var(--heading-border); padding-bottom: 0.25em; }
h3 { font-size: 1.25em; }
h4 { font-size: 1.1em; }
h5 { font-size: 1em; }
h6 { font-size: 0.875em; color: var(--text-secondary); }

p { margin: 0.75em 0; }

a { color: var(--link-color); text-decoration: none; }
a:hover { color: var(--link-hover); text-decoration: underline; }

strong { font-weight: 600; }
em { font-style: italic; }

/* ===== Blockquote ===== */
blockquote {
  border-left: 4px solid var(--blockquote-border);
  background: var(--blockquote-bg);
  padding: 0.75em 1em;
  margin: 1em 0;
  border-radius: 0 var(--radius) var(--radius) 0;
  color: var(--text-secondary);
}
blockquote p:first-child { margin-top: 0; }
blockquote p:last-child { margin-bottom: 0; }

/* ===== Code ===== */
code {
  font-family: var(--font-mono);
  font-size: 0.875em;
  background: var(--code-bg);
  color: var(--code-text);
  padding: 0.15em 0.4em;
  border-radius: 4px;
}

pre {
  font-family: var(--font-mono);
  font-size: 0.875em;
  background: var(--code-bg);
  color: var(--code-text);
  padding: 1em;
  border-radius: var(--radius);
  overflow-x: auto;
  line-height: 1.5;
  margin: 1em 0;
  tab-size: 2;
}
pre code {
  background: none;
  padding: 0;
  font-size: inherit;
  color: inherit;
}

/* ===== Lists ===== */
ul, ol { margin: 0.5em 0 0.5em 1.5em; padding: 0; }
li { margin: 0.25em 0; }
li > ul, li > ol { margin: 0.25em 0 0.25em 1.5em; }

/* ===== Tables ===== */
.table-wrapper {
  overflow-x: auto;
  margin: 1em 0;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  -webkit-overflow-scrolling: touch;
}

/* Scrollbar styling for webkit */
.table-wrapper::-webkit-scrollbar {
  height: 6px;
}
.table-wrapper::-webkit-scrollbar-track {
  background: transparent;
}
.table-wrapper::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 3px;
}
.table-wrapper::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}

/* Vertical scroll for very tall tables */
.table-wrapper.tall {
  max-height: 70vh;
  overflow-y: auto;
}

/* Sticky header when vertical scroll is on */
.table-wrapper.tall thead {
  position: sticky;
  top: 0;
  z-index: 1;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9375em;
}

thead { background: var(--accent); color: var(--accent-text); }
th, td {
  padding: 0.6em 0.8em;
  text-align: left;
  border: 1px solid var(--border);
  white-space: nowrap;
}
th { font-weight: 600; letter-spacing: 0.01em; }
tbody tr:nth-child(even) { background: var(--table-stripe); }
tbody tr:hover { background: var(--table-hover); }

/* ===== Horizontal Rule ===== */
hr {
  border: none;
  border-top: 1px solid var(--hr-color);
  margin: 2em 0;
}

/* ===== Images ===== */
img {
  max-width: 100%;
  height: auto;
  border-radius: var(--radius);
  box-shadow: var(--img-shadow);
  display: block;
  margin: 1em auto;
}

/* ===== KBD ===== */
kbd {
  font-family: var(--font-mono);
  font-size: 0.8em;
  background: var(--kbd-bg);
  border: 1px solid var(--kbd-border);
  border-radius: 4px;
  padding: 0.15em 0.5em;
  box-shadow: 0 1px 0 var(--kbd-border);
}

/* ===== Mark ===== */
mark {
  background: var(--mark-bg);
  color: inherit;
  padding: 0.1em 0.3em;
  border-radius: 3px;
}

/* ===== Details / Summary ===== */
details {
  margin: 1em 0;
  padding: 0.5em 1em;
  background: var(--blockquote-bg);
  border-radius: var(--radius);
  border: 1px solid var(--border);
}
summary {
  font-weight: 600;
  cursor: pointer;
  padding: 0.25em 0;
}
summary:hover { color: var(--accent); }

/* ===== Task List (Github-Flavored) ===== */
ul.task-list { list-style: none; margin-left: 0; }
.task-list-item { display: flex; align-items: flex-start; gap: 0.5em; }
.task-list-item input[type="checkbox"] {
  margin-top: 0.35em;
  accent-color: var(--accent);
  width: 1.1em;
  height: 1.1em;
  flex-shrink: 0;
}

/* ===== Footnotes ===== */
.footnotes { margin-top: 2em; padding-top: 1em; border-top: 1px solid var(--border); font-size: 0.875em; color: var(--text-secondary); }
.footnotes ol { margin-left: 1.5em; }
.footnotes li { margin: 0.3em 0; }

/* ===== Print ===== */
@media print {
  body { background: white; padding: 0; }
  .container { box-shadow: none; border-radius: 0; padding: 0; }
  pre { white-space: pre-wrap; word-break: break-word; }
  table { page-break-inside: auto; }
  tr { page-break-inside: avoid; }
  h1, h2, h3, h4 { page-break-after: avoid; }
}

/* ===== Responsive ===== */
@media (max-width: 640px) {
  body { padding: 0.75rem; }
  .container { padding: 1rem 0.75rem; border-radius: var(--radius); }
  h1 { font-size: 1.5em; }
  h2 { font-size: 1.25em; }
  h3 { font-size: 1.1em; }
  th, td { padding: 0.4em 0.5em; font-size: 0.875em; }
  pre { font-size: 0.8em; }
  th, td { padding: 0.4em 0.5em; font-size: 0.85em; }
}

@media (min-width: 640px) and (max-width: 1024px) {
  body { padding: 1.5rem; }
  .container { padding: 1.5rem; }
}
"""

# ──────────────────────────────────────────────
# HTML Template
# ──────────────────────────────────────────────
HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="generator" content="md2html">
<title>{title}</title>
<style>
{style}
</style>
</head>
<body>
<div class="container">
<article>
{content}
</article>
<footer style="margin-top:3em;padding-top:1em;border-top:1px solid var(--border);font-size:0.8em;color:var(--text-secondary);text-align:center;">
  Generated by <strong>md2html</strong>
  &mdash; {source_file}
</footer>
</div>
</body>
</html>"""


# ──────────────────────────────────────────────
# Markdown Renderer
# ──────────────────────────────────────────────
def make_md_engine() -> MarkdownIt:
    """Create a markdown-it engine with all the goodies enabled."""
    md = MarkdownIt("js-default", {
        "breaks": True,
        "html": True,
        "linkify": True,
        "typographer": True,
    })
    # Built-in rules
    md.enable("table")
    md.enable("strikethrough")
    # mdit-py-plugins (optional)
    if HAS_DEFLIST:
        md.use(deflist_plugin)
    if HAS_FOOTNOTE:
        md.use(footnote_plugin)
    if HAS_SUBSCRIPT:
        md.use(sub_plugin)
    if HAS_SUPERSCRIPT:
        md.use(superscript_plugin)
    if HAS_TASKLISTS:
        md.use(tasklists_plugin)
    return md


def mermaid_cleanup(html: str) -> str:
    """
    Remove empty <p> tags around mermaid code blocks
    (markdown-it wraps code blocks in <p> when inside a <pre>).
    """
    # Remove stray <p></p> that wrap around code block outputs
    html = re.sub(r'<p>\s*</p>', '', html)
    return html


def wrap_tables(html: str) -> str:
    """Wrap every <table> in a scrollable container so wide tables
    get horizontal scrollbars instead of overflowing the viewport.
    Tall tables (>15 rows) also get a max-height vertical scroll."""

    def _wrapper(match: re.Match) -> str:
        table_html = match.group(0)
        # Count <tr> to decide if vertical scroll is needed
        row_count = table_html.count('<tr>')
        tall_class = ' tall' if row_count > 15 else ''
        return f'<div class="table-wrapper{tall_class}">{table_html}</div>'

    return re.sub(r'<table>.*?</table>', _wrapper, html, flags=re.DOTALL)


def convert_md_to_html(md_text: str) -> str:
    """Convert raw Markdown text to clean HTML body."""
    md = make_md_engine()
    html = md.render(md_text)
    html = mermaid_cleanup(html)
    html = wrap_tables(html)
    return html


def extract_title(md_text: str, source_path: Path) -> str:
    """Extract the first H1 (# Title) from the markdown, else use filename."""
    for line in md_text.splitlines():
        line = line.strip()
        if line.startswith("# ") and not line.startswith("##"):
            return line[2:].strip()
    # Fall back to filename without extension
    return source_path.stem


def detect_lang(md_text: str) -> str:
    """Detect if the document is primarily Chinese."""
    # Simple heuristic: count CJK characters in first 500 chars
    sample = md_text[:500]
    cjk_count = sum(1 for c in sample if '\u4e00' <= c <= '\u9fff' or '\u3000' <= c <= '\u303f')
    total = len(sample.strip())
    if total > 0 and cjk_count / total > 0.1:
        return "zh-CN"
    return "en"


def generate_html(md_text: str, source_path: Path) -> str:
    """Full pipeline: markdown -> HTML body -> wrapped document."""
    title = extract_title(md_text, source_path)
    lang = detect_lang(md_text)
    content = convert_md_to_html(md_text)
    source_name = source_path.name

    return HTML_TEMPLATE.format(
        title=xml_escape(title),
        lang=lang,
        style=STYLE_CSS,
        content=content,
        source_file=xml_escape(source_name),
    )


# ──────────────────────────────────────────────
# File I/O
# ──────────────────────────────────────────────
def resolve_output_path(source: Path, output_dir: Path | None, inplace: bool) -> Path:
    """Determine where the .html file should be written."""
    if inplace:
        return source.with_suffix(".html")
    if output_dir:
        out = output_dir / source.with_suffix(".html").name
        return out
    return source.with_suffix(".html")


def process_file(source: Path, output_dir: Path | None, inplace: bool, verbose: bool, pdf_mode: str = "") -> bool:
    """Convert a single .md file to .html (and optionally .pdf).
    pdf_mode: "" = no PDF, "a4" = standard A4, "wechat" = mobile-optimized.
    Returns True on success."""
    if not source.exists():
        print(f"  ERROR: NOT FOUND: {source}")
        return False
    if source.suffix.lower() not in (".md", ".markdown"):
        if verbose:
            print(f"  [>>]  SKIP (not .md): {source}")
        return True  # Not an error, just skipped

    try:
        md_text = source.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  ERROR: READ ERROR: {source}: {e}")
        return False

    try:
        html = generate_html(md_text, source)
    except Exception as e:
        print(f"  ERROR: CONVERSION ERROR: {source}: {e}")
        return False

    out_path = resolve_output_path(source, output_dir, inplace)

    # Create parent directories if needed
    out_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        out_path.write_text(html, encoding="utf-8")
        msg = f"  OK {source.name} -> {out_path.name}  ({len(html):,}B)"
        if pdf_mode:
            pdf_path = out_path.with_suffix(".pdf") if pdf_mode == "a4" else out_path.with_suffix(".wechat.pdf")
            wechat = (pdf_mode == "wechat")
            if render_pdf(out_path, pdf_path, verbose, wechat=wechat):
                pdf_size = pdf_path.stat().st_size
                msg += f" + {pdf_path.name} ({pdf_size:,}B)"
            else:
                msg += " (PDF FAILED)"
        print(msg)
        return True
    except Exception as e:
        print(f"  ERROR: WRITE ERROR: {out_path}: {e}")
        return False


# ──────────────────────────────────────────────
# PDF common CSS fixes (injected for all PDF renders)
# Fixes: table page-break etiquette + wide-table text wrapping
# ──────────────────────────────────────────────
PDF_TABLE_FIX = """
/* === PDF table fixes === */
th, td {
  white-space: normal !important;
  word-break: break-word;
  overflow-wrap: break-word;
}

tr {
  page-break-inside: avoid;
  break-inside: avoid;
}

thead {
  display: table-header-group;
}

thead tr {
  page-break-inside: avoid;
  break-inside: avoid;
}

/* Give tables breathing room before page breaks */
.table-wrapper {
  page-break-inside: auto;
  break-inside: auto;
}
"""

# ──────────────────────────────────────────────
# WeChat mobile-reading CSS overrides (injected before PDF render)
# ──────────────────────────────────────────────
WECHAT_CSS_OVERRIDE = """
/* === WeChat mobile reading overrides === */
body {
  font-size: 18px;
  line-height: 1.85;
  padding: 8px 4px;
}
.container {
  max-width: 100%;
  padding: 10px 8px;
  box-shadow: none;
  border-radius: 0;
}
h1 { font-size: 1.55em; }
h2 { font-size: 1.3em; }
h3 { font-size: 1.15em; }
pre { font-size: 0.85em; }
th, td {
  font-size: 0.92em;
  padding: 5px 7px;
}
table { font-size: 0.9em; }
"""


def render_pdf(html_path: Path, pdf_path: Path, verbose: bool = False, wechat: bool = False) -> bool:
    """Render a self-contained HTML file to PDF via WeasyPrint.
    Standard mode: A4 with @media print CSS.
    WeChat mode: narrow page, larger text, continuous tall pages."""
    try:
        from weasyprint import HTML
    except ImportError:
        if verbose:
            print("    PDF requires `weasyprint`: pip install weasyprint")
        return False

    try:
        html_text = html_path.read_text(encoding="utf-8")

        if wechat:
            # Inject wechat overrides + table fix + narrow page inside @media print
            # (WeasyPrint uses print media — wrap in @media print to override originals)
            inject_css = (
                "@media print {"
                + WECHAT_CSS_OVERRIDE
                + PDF_TABLE_FIX
                + "}\n"
                + "@page { size: 108mm 1000mm; margin: 6mm 5mm; }"
            )
        else:
            # A4: inject table fix + explicit page definition
            inject_css = (
                "@media print {"
                + PDF_TABLE_FIX
                + "}\n"
                + "@page { size: A4; margin: 15mm 12mm; }"
            )

        html_text = html_text.replace("</style>", inject_css + "\n</style>")
        HTML(string=html_text).write_pdf(str(pdf_path))
        return True
    except Exception as e:
        if verbose:
            print(f"    PDF render error: {e}")
        return False


def discover_md_files(paths: list[Path]) -> list[Path]:
    """Resolve paths: files directly, directories scanned recursively."""
    files: list[Path] = []
    for p in paths:
        if p.is_file():
            files.append(p)
        elif p.is_dir():
            # Walk directories recursively
            files.extend(sorted(p.rglob("*.md")))
            files.extend(sorted(p.rglob("*.markdown")))
        else:
            print(f"  WARN:  Not found: {p}")
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for f in files:
        resolved = f.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(f)
    return unique


# ──────────────────────────────────────────────
# Watch Mode
# ──────────────────────────────────────────────
def watch_and_build(watch_paths: list[Path], output_dir: Path | None, inplace: bool, verbose: bool, pdf_mode: str = ""):
    """Watch directories for .md changes and rebuild automatically."""
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        print("Watch mode requires `watchdog`: pip install watchdog")
        sys.exit(1)

    # Initial build
    print("=== Initial Build ===")
    files = discover_md_files(watch_paths)
    for f in files:
        process_file(f, output_dir, inplace, verbose, pdf_mode)
    print(f"Watching {len(watch_paths)} path(s) for changes... (Ctrl+C to stop)")

    class MDHandler(FileSystemEventHandler):
        def on_modified(self, event):
            if event.is_directory:
                return
            src = Path(event.src_path)
            if src.suffix.lower() in (".md", ".markdown"):
                if verbose:
                    print(f"\n  CHANGED: Changed: {src.name}")
                process_file(src, output_dir, inplace, verbose, pdf_mode)
                print(f"  OK Rebuilt: {src.stem}.html")

    handler = MDHandler()
    observers = []
    for wp in watch_paths:
        if wp.is_dir():
            observer = Observer()
            observer.schedule(handler, str(wp), recursive=True)
            observer.start()
            observers.append(observer)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        for o in observers:
            o.stop()
        for o in observers:
            o.join()


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Batch Markdown -> Self-Contained HTML Converter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("\n\n")[1],  # usage examples
    )
    parser.add_argument("paths", nargs="+", type=Path,
                        help="One or more .md files or directories")
    parser.add_argument("-o", "--output", type=Path, default=None,
                        help="Output directory (default: alongside source)")
    parser.add_argument("--inplace", action="store_true",
                        help="Write .html next to each .md file (sibling)")
    parser.add_argument("--pdf", action="store_true",
                        help="Also generate standard A4 PDF (requires playwright)")
    parser.add_argument("--wechat", action="store_true",
                        help="Also generate mobile-optimized PDF for WeChat reading")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Verbose output")
    parser.add_argument("--watch", action="store_true",
                        help="Watch for changes and auto-rebuild (requires watchdog)")
    parser.add_argument("--quiet", action="store_true",
                        help="Only print errors")

    args = parser.parse_args()

    # Validate
    if args.inplace and args.output:
        print("Error: --inplace and --output are mutually exclusive.")
        sys.exit(1)

    inplace = args.inplace if args.inplace else (args.output is None)
    # pdf_mode: "" = no PDF, "a4" = standard, "wechat" = mobile-optimized
    if args.wechat:
        pdf_mode = "wechat"
    elif args.pdf:
        pdf_mode = "a4"
    else:
        pdf_mode = ""

    files = discover_md_files(args.paths)
    if not files:
        print("No .md files found. Exiting.")
        sys.exit(0)

    if args.watch:
        watch_and_build(args.paths, args.output, inplace, args.verbose and not args.quiet, pdf_mode)
        return

    # Batch build
    success = 0
    failed = 0
    skipped = 0
    for f in files:
        ok = process_file(f, args.output, inplace, args.verbose or not args.quiet, pdf_mode)
        if ok:
            success += 1
        else:
            failed += 1

    total = len(files)
    if not args.quiet:
        print(f"\n{'='*40}")
        print(f"Done: {success}/{total} files converted")
        if pdf_mode:
            print("(HTML + PDF generated — send .pdf via WeChat for inline preview)")

    if args.output:
        print(f"Output: {args.output.resolve()}")
    if failed:
        print(f"Failed: {failed}")
        sys.exit(1)


if __name__ == "__main__":
    main()
