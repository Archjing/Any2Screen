from pathlib import Path

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
    # 使用 WeasyPrint 将 HTML 文件渲染为标准或微信阅读 PDF。
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


def render_image(
    html_path: Path,
    image_path: Path,
    width: int,
    image_format: str,
    verbose: bool = False,
) -> tuple[bool, int, int, int]:
    # 使用 Playwright 将 HTML 文件截取为长图。
    """Render a self-contained HTML file to a long image via Playwright."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        if verbose:
            print("    Image output requires `playwright`: uv run playwright install chromium")
        return False, 0, width, 0

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": width, "height": 800})
            page.goto(f"file://{html_path}", wait_until="networkidle")

            height = page.evaluate("document.body.scrollHeight")
            page.set_viewport_size({"width": width, "height": height + 40})
            screenshot_kwargs = {
                "path": str(image_path),
                "full_page": True,
                "type": image_format,
            }
            if image_format == "jpeg":
                # 提高 JPEG 编码质量，减少大屏长图的压缩模糊。
                screenshot_kwargs["quality"] = 95
            page.screenshot(**screenshot_kwargs)
            browser.close()

        return True, image_path.stat().st_size, width, height + 40
    except Exception as e:
        if verbose:
            print(f"    Image render error: {e}")
        return False, 0, width, 0
