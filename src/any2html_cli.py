#!/usr/bin/env python3
import argparse
from pathlib import Path
import sys

from any2html import generate_html


def discover_input_files(paths: list[Path]) -> list[Path]:
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


def resolve_output_path(source: Path, output: Path | None) -> Path:
    if output is None:
        return source.with_suffix(".html")
    if output.suffix and len(output.suffix) > 1:
        return output
    return output / source.with_suffix(".html").name


def convert_file(source: Path, output: Path | None) -> bool:
    if source.suffix.lower() not in (".md", ".markdown"):
        print(f"  ERROR: unsupported input format: {source}")
        return False
    try:
        html = generate_html(source.read_text(encoding="utf-8"), source)
        out_path = resolve_output_path(source, output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html, encoding="utf-8")
        print(f"  OK {source.name} -> {out_path.name} ({len(html):,}B)")
        return True
    except Exception as e:
        print(f"  ERROR: {source}: {e}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert supported document formats to HTML intermediate output",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python3 scripts/any2screen.py any2html README.md
  python3 scripts/any2screen.py any2html README.md -o exports/
  python3 scripts/any2screen.py any2html README.md -o exports/readme.html
""",
    )
    parser.add_argument("paths", nargs="+", type=Path, help="Input files or directories")
    parser.add_argument("-o", "--output", type=Path, default=None,
                        help="Output HTML file or directory (default: alongside source)")
    args = parser.parse_args()

    files = discover_input_files(args.paths)
    if not files:
        print("No supported input files found. Exiting.")
        return 0
    if args.output and args.output.suffix and len(files) > 1:
        print("Error: file output path can only be used with one input file.")
        return 1

    success = sum(1 for f in files if convert_file(f, args.output))
    failed = len(files) - success
    print(f"\nDone: {success}/{len(files)} files converted")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
