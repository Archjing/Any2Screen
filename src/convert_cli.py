#!/usr/bin/env python3
import argparse
from pathlib import Path
import tempfile

from any2html import generate_html
from html2screen_cli import process_file as html2screen_process_file


def discover_input_files(paths: list[Path]) -> list[Path]:
    # 从输入路径中收集主转换 pipeline 支持的 Markdown 文件。
    files: list[Path] = []
    for p in paths:
        if p.is_file():
            files.append(p)
        elif p.is_dir():
            files.extend(sorted(p.rglob("*.md")))
            files.extend(sorted(p.rglob("*.markdown")))
        else:
            print(f"  WARN:  Not found: {p}")
    return files


def write_intermediate_html(source: Path, intermediate_dir: Path) -> Path:
    # 把 Markdown 输入写成临时 HTML 中间文件供后续渲染使用。
    if source.suffix.lower() not in (".md", ".markdown"):
        raise ValueError(f"unsupported input format: {source}")
    html = generate_html(source.read_text(encoding="utf-8"), source)
    html_path = intermediate_dir / source.with_suffix(".html").name
    html_path.write_text(html, encoding="utf-8")
    return html_path


def main() -> int:
    # 解析 convert 命令参数并执行 any2html 到 html2screen 的完整流程。
    parser = argparse.ArgumentParser(
        description="Run any2html -> html2screen pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python3 scripts/any2screen.py convert README.md
  python3 scripts/any2screen.py convert README.md --pdf
  python3 scripts/any2screen.py convert README.md --img --width 960 --format png
  python3 scripts/any2screen.py convert README.md --html --pdf --wechat --img -o exports/

Output rules:
  - No output flag: HTML only.
  - Any output flag: only the requested format(s).
  - -o/--output is an output directory for all generated files.
""",
    )
    parser.add_argument("paths", nargs="+", type=Path, help="Input files or directories")
    parser.add_argument("-o", "--output", type=Path, default=None,
                        help="Output directory (default: alongside source)")
    parser.add_argument("--html", action="store_true",
                        help="Generate HTML output. Default unless any output flag is used")
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

    files = discover_input_files(args.paths)
    if not files:
        print("No supported input files found. Exiting.")
        return 0

    output_requested = args.html or args.pdf or args.wechat or args.img
    write_html = args.html or not output_requested
    success = 0

    for source in files:
        try:
            with tempfile.TemporaryDirectory(prefix="any2screen-") as tmp:
                intermediate = write_intermediate_html(source, Path(tmp))
                output_dir = args.output or source.parent
                if html2screen_process_file(
                    intermediate,
                    output_dir,
                    write_html,
                    args.pdf,
                    args.wechat,
                    args.img,
                    args.width,
                    args.format,
                    args.verbose,
                ):
                    success += 1
        except Exception as e:
            print(f"  ERROR: {source}: {e}")

    failed = len(files) - success
    print(f"\nDone: {success}/{len(files)} files converted")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
