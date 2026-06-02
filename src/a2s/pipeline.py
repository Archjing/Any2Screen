import tempfile
from pathlib import Path

from a2s.any2html import generate_html
from a2s.html2screen import render_image, render_pdf


def resolve_output_path(source: Path, output_dir: Path | None, inplace: bool) -> Path:
    """Determine where the intermediate .html path maps for output naming."""
    if inplace:
        return source.with_suffix(".html")
    if output_dir:
        return output_dir / source.with_suffix(".html").name
    return source.with_suffix(".html")


def convert_markdown_file(
    source: Path,
    output_dir: Path | None,
    inplace: bool,
    verbose: bool,
    pdf_mode: str = "",
    write_html: bool = True,
    write_img: bool = False,
    image_width: int = 960,
    image_format: str = "png",
) -> bool:
    """Run any2html -> html2screen for one Markdown file."""
    if not source.exists():
        print(f"  ERROR: NOT FOUND: {source}")
        return False
    if source.suffix.lower() not in (".md", ".markdown"):
        if verbose:
            print(f"  [>>]  SKIP (not .md): {source}")
        return True

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

    html_path = resolve_output_path(source, output_dir, inplace)
    html_path.parent.mkdir(parents=True, exist_ok=True)

    temp_render_path = None
    try:
        outputs = []
        render_source = html_path

        if write_html:
            html_path.write_text(html, encoding="utf-8")
            outputs.append(f"{html_path.name} ({len(html):,}B)")

        if (pdf_mode or write_img) and not write_html:
            with tempfile.NamedTemporaryFile(
                "w",
                suffix=".html",
                encoding="utf-8",
                dir=html_path.parent,
                delete=False,
            ) as tmp:
                tmp.write(html)
                temp_render_path = Path(tmp.name)
                render_source = temp_render_path

        for mode in [mode for mode in pdf_mode.split(",") if mode]:
            pdf_path = html_path.with_suffix(".pdf") if mode == "a4" else html_path.with_suffix(".wechat.pdf")
            wechat = mode == "wechat"
            if render_pdf(render_source, pdf_path, verbose, wechat=wechat):
                outputs.append(f"{pdf_path.name} ({pdf_path.stat().st_size:,}B)")
            else:
                outputs.append("PDF FAILED")

        if write_img:
            img_path = html_path.with_suffix(f".{image_format}")
            img_path.parent.mkdir(parents=True, exist_ok=True)
            ok, img_size, width, height = render_image(render_source, img_path, image_width, image_format, verbose)
            if ok:
                outputs.append(f"{img_path.name} ({img_size:,}B, {width}x{height})")
            else:
                outputs.append("IMG FAILED")

        print(f"  OK {source.name} -> " + " + ".join(outputs))
        return True
    except Exception as e:
        print(f"  ERROR: WRITE ERROR: {html_path}: {e}")
        return False
    finally:
        if temp_render_path and temp_render_path.exists():
            temp_render_path.unlink()
