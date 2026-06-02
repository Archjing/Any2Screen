#!/usr/bin/env python3
import argparse
import shutil
from pathlib import Path

from a2s.html2screen import render_image, render_pdf


def discover_html_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for p in paths:
        if p.is_file():
            files.append(p)
        elif p.is_dir():
            files.extend(sorted(p.rglob("*.html")))
        else:
            print(f"  WARN:  Not found: {p}")
    return files


def resolve_output_path(source: Path, output_dir: Path | None) -> Path:
    if output_dir:
        return output_dir / source.name
    return source


def process_file(
    source: Path,
    output_dir: Path | None,
    write_html: bool,
    write_pdf: bool,
    write_wechat: bool,
    write_img: bool,
    width: int,
    image_format: str,
    verbose: bool,
) -> bool:
    if source.suffix.lower() not in (".html", ".htm"):
        print(f"  ERROR: unsupported input format: {source}")
        return False

    out_html = resolve_output_path(source, output_dir)
    out_html.parent.mkdir(parents=True, exist_ok=True)
    outputs = []

    try:
        render_source = source
        if write_html:
            if out_html.resolve() != source.resolve():
                shutil.copyfile(source, out_html)
            outputs.append(f"{out_html.name} ({out_html.stat().st_size:,}B)")
            render_source = out_html

        base_path = out_html
        if write_pdf:
            pdf_path = base_path.with_suffix(".pdf")
            if render_pdf(render_source, pdf_path, verbose, wechat=False):
                outputs.append(f"{pdf_path.name} ({pdf_path.stat().st_size:,}B)")
            else:
                outputs.append("PDF FAILED")

        if write_wechat:
            wechat_path = base_path.with_suffix(".wechat.pdf")
            if render_pdf(render_source, wechat_path, verbose, wechat=True):
                outputs.append(f"{wechat_path.name} ({wechat_path.stat().st_size:,}B)")
            else:
                outputs.append("WECHAT PDF FAILED")

        if write_img:
            img_path = base_path.with_suffix(f".{image_format}")
            ok, img_size, img_width, height = render_image(render_source, img_path, width, image_format, verbose)
            if ok:
                outputs.append(f"{img_path.name} ({img_size:,}B, {img_width}x{height})")
            else:
                outputs.append("IMG FAILED")

        print(f"  OK {source.name} -> " + " + ".join(outputs))
        return True
    except Exception as e:
        print(f"  ERROR: {source}: {e}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert HTML intermediate output to screen-friendly formats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python3 scripts/any2screen.py html2screen README.html --pdf
  python3 scripts/any2screen.py html2screen README.html --wechat
  python3 scripts/any2screen.py html2screen README.html --img --width 960 --format png
  python3 scripts/any2screen.py html2screen README.html --html --pdf --wechat --img -o exports/

Output rules:
  - No output flag: mobile/self-contained HTML copy only.
  - Any output flag: only the requested format(s).
  - -o/--output is an output directory for all generated files.
""",
    )
    parser.add_argument("paths", nargs="+", type=Path, help="HTML files or directories")
    parser.add_argument("-o", "--output", type=Path, default=None,
                        help="Output directory (default: alongside source)")
    parser.add_argument("--html", action="store_true",
                        help="Write/copy HTML output. Default unless any output flag is used")
    parser.add_argument("--pdf", action="store_true", help="Generate standard A4 PDF output")
    parser.add_argument("--wechat", action="store_true", help="Generate mobile-optimized WeChat PDF output")
    parser.add_argument("--img", action="store_true", help="Generate long image output")
    parser.add_argument("--width", type=int, default=960,
                        help="Image viewport width in pixels (default: 960)")
    parser.add_argument("--format", choices=("png", "jpeg"), default="png",
                        help="Image output format for --img (default: png)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    if args.width < 320:
        print("Error: --width must be at least 320.")
        return 1

    files = discover_html_files(args.paths)
    if not files:
        print("No HTML files found. Exiting.")
        return 0

    output_requested = args.html or args.pdf or args.wechat or args.img
    write_html = args.html or not output_requested

    success = 0
    for f in files:
        if process_file(f, args.output, write_html, args.pdf, args.wechat, args.img, args.width, args.format, args.verbose):
            success += 1
    failed = len(files) - success
    print(f"\nDone: {success}/{len(files)} files converted")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
