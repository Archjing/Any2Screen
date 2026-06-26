#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from perf_baseline import (
    dump_json,
    build_default_scenarios,
    render_markdown_report,
    run_scenario,
    summarize_local_environment,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect Any2Screen performance baseline")
    parser.add_argument(
        "--environment",
        default="local",
        choices=("local", "docker"),
        help="Environment label recorded in the report",
    )
    parser.add_argument(
        "--python",
        default=".venv/bin/python",
        help="Python executable used to run Any2Screen commands",
    )
    parser.add_argument(
        "--sample-root",
        type=Path,
        default=Path("samples/perf-baseline"),
        help="Sample input root for generated baseline fixtures",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("docs/performance-baseline.md"),
        help="Markdown report output path",
    )
    parser.add_argument(
        "--json",
        type=Path,
        default=Path("docs/performance-baseline.json"),
        help="JSON report output path",
    )
    parser.add_argument(
        "--runtime",
        default="uv run",
        help="Runtime label written into the environment section",
    )
    parser.add_argument(
        "--notes",
        default="Collected from the repository root with generated baseline fixtures.",
        help="Extra notes written into the environment section",
    )
    args = parser.parse_args()

    repo_root = ROOT
    scenarios = build_default_scenarios(repo_root / args.sample_root)
    results = [run_scenario(repo_root, scenario, python_executable=args.python) for scenario in scenarios]
    environment = summarize_local_environment(args.environment, args.runtime, args.notes)
    grouped_results = {args.environment: results}
    docker_command = (
        "docker compose -f Any2Screen-server/docker-compose.yml run --rm "
        "any2screen-api python scripts/collect_performance_baseline.py "
        "--environment docker --python python --runtime docker "
        '--notes "Collected inside any2screen-api container"'
    )

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        render_markdown_report(
            environments=[environment],
            grouped_results=grouped_results,
            docker_command=docker_command,
        ),
        encoding="utf-8",
    )
    dump_json(args.json, [environment], grouped_results)

    failed = [result for result in results if not result.success]
    print(f"Collected {len(results)} scenarios for {args.environment}. Report: {args.report}")
    if failed:
        print(f"{len(failed)} scenario(s) failed.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
