#!/usr/bin/env python3
import argparse
from pathlib import Path

from preview import PreviewOptions, generate_preview_html


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
        return source.with_suffix(".preview.html")
    if output.suffix and len(output.suffix) > 1:
        return output
    return output / source.with_suffix(".preview.html").name


def preview_file(source: Path, output: Path | None, options: PreviewOptions) -> bool:
    if source.suffix.lower() not in (".md", ".markdown"):
        print(f"  ERROR: unsupported input format: {source}")
        return False

    try:
        html, result = generate_preview_html(source.read_text(encoding="utf-8"), source, options)
        out_path = resolve_output_path(source, output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html, encoding="utf-8")
        suffix = " truncated" if result.truncated else " complete"
        print(
            f"  OK {source.name} -> {out_path.name} "
            f"({result.included_blocks}/{result.total_blocks} blocks,{suffix})"
        )
        return True
    except Exception as e:
        print(f"  ERROR: {source}: {e}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate fast lightweight HTML previews for supported documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python3 scripts/any2screen.py preview README.md
  python3 scripts/any2screen.py preview README.md --blocks 12
  python3 scripts/any2screen.py preview ./notes -o ./previews
""",
    )
    parser.add_argument("paths", nargs="+", type=Path, help="Input Markdown files or directories")
    parser.add_argument("-o", "--output", type=Path, default=None,
                        help="Output HTML file or directory (default: alongside source)")
    parser.add_argument("--blocks", type=int, default=20,
                        help="Maximum Markdown blocks to include (default: 20)")
    parser.add_argument("--table-rows", type=int, default=20,
                        help="Maximum data rows per table (default: 20)")
    parser.add_argument("--code-lines", type=int, default=120,
                        help="Maximum lines per fenced code block (default: 120)")
    args = parser.parse_args()

    if args.blocks < 1:
        print("Error: --blocks must be at least 1.")
        return 1
    if args.table_rows < 1:
        print("Error: --table-rows must be at least 1.")
        return 1
    if args.code_lines < 1:
        print("Error: --code-lines must be at least 1.")
        return 1

    files = discover_input_files(args.paths)
    if not files:
        print("No supported input files found. Exiting.")
        return 0
    if args.output and args.output.suffix and len(files) > 1:
        print("Error: file output path can only be used with one input file.")
        return 1

    options = PreviewOptions(
        max_blocks=args.blocks,
        max_table_rows=args.table_rows,
        max_code_lines=args.code_lines,
    )
    success = sum(1 for f in files if preview_file(f, args.output, options))
    failed = len(files) - success
    print(f"\nDone: {success}/{len(files)} previews generated")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
