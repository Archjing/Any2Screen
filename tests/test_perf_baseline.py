from __future__ import annotations

import unittest
from pathlib import Path

from tests import _paths  # noqa: F401
from perf_baseline import EnvironmentSummary, ScenarioResult, build_default_scenarios, render_markdown_report


class PerfBaselineTests(unittest.TestCase):
    def test_default_scenarios_cover_d5_baseline_matrix(self) -> None:
        scenarios = build_default_scenarios(Path("samples/perf-baseline"))

        scenario_ids = {scenario.scenario_id for scenario in scenarios}
        input_kinds = {scenario.input_kind for scenario in scenarios}
        output_formats = {scenario.output_format for scenario in scenarios}
        stage_categories = {scenario.stage_category for scenario in scenarios}

        self.assertEqual(
            scenario_ids,
            {
                "markdown-html",
                "text-html",
                "docx-html",
                "pdf-html",
                "markdown-pdf-a4",
                "markdown-pdf-wechat",
                "markdown-image-small-png",
                "markdown-image-large-jpeg",
            },
        )
        self.assertEqual(input_kinds, {"markdown", "text", "docx", "pdf"})
        self.assertEqual(output_formats, {"html", "pdf", "wechat-pdf", "png", "jpeg"})
        self.assertEqual(stage_categories, {"html_generation", "pdf_render", "image_render"})

    def test_markdown_report_contains_environment_results_and_regression_policy(self) -> None:
        environment = EnvironmentSummary(
            name="local",
            recorded_at="2026-06-25T22:30:00+08:00",
            machine="Linux-6.8-x86_64",
            python_version="3.12.9",
            runtime="uv run",
            notes="Playwright Chromium preinstalled",
        )
        results = [
            ScenarioResult(
                scenario_id="markdown-html",
                title="Markdown -> HTML",
                stage_category="html_generation",
                input_kind="markdown",
                output_format="html",
                command="uv run python scripts/any2screen.py any2html samples/perf-baseline/inputs/article.md -o tmp",
                success=True,
                duration_seconds=0.412,
                output_bytes=5234,
                output_width=430,
                output_height=0,
                output_pages=None,
                output_path="tmp/article.html",
                error_message="",
            )
        ]

        report = render_markdown_report(
            environments=[environment],
            grouped_results={"local": results},
            docker_command="docker compose -f Any2Screen-server/docker-compose.yml run --rm any2screen-api ...",
        )

        self.assertIn("# Any2Screen Performance Baseline", report)
        self.assertIn("2026-06-25T22:30:00+08:00", report)
        self.assertIn("markdown-html", report)
        self.assertIn("0.412", report)
        self.assertIn("5234", report)
        self.assertIn("D27", report)
        self.assertIn("20%", report)
        self.assertIn("docker compose -f Any2Screen-server/docker-compose.yml run --rm any2screen-api", report)


if __name__ == "__main__":
    unittest.main()
