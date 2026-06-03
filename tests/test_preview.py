import tempfile
import unittest
from pathlib import Path

from tests import _paths  # noqa: F401
from preview import PreviewOptions, build_markdown_preview, generate_preview_html
from preview_cli import discover_input_files, resolve_output_path


class PreviewTests(unittest.TestCase):
    def test_build_markdown_preview_limits_by_blocks(self) -> None:
        markdown = "# Title\n\nFirst paragraph.\n\n## Later\n\nSecond paragraph.\n"

        result = build_markdown_preview(markdown, PreviewOptions(max_blocks=2))

        self.assertTrue(result.truncated)
        self.assertEqual(result.total_blocks, 4)
        self.assertEqual(result.included_blocks, 2)
        self.assertIn("# Title", result.markdown)
        self.assertIn("First paragraph.", result.markdown)
        self.assertNotIn("## Later", result.markdown)

    def test_build_markdown_preview_limits_table_rows(self) -> None:
        rows = "\n".join(f"| {i} | value |" for i in range(5))
        markdown = f"| A | B |\n|---|---|\n{rows}\n\nAfter"

        result = build_markdown_preview(markdown, PreviewOptions(max_blocks=5, max_table_rows=2))

        self.assertTrue(result.truncated)
        self.assertIn("| 0 | value |", result.markdown)
        self.assertIn("| 1 | value |", result.markdown)
        self.assertNotIn("| 2 | value |", result.markdown)
        self.assertIn("After", result.markdown)

    def test_build_markdown_preview_limits_fenced_code_lines(self) -> None:
        markdown = "```python\nline1\nline2\nline3\n```\n\nAfter"

        result = build_markdown_preview(markdown, PreviewOptions(max_blocks=5, max_code_lines=2))

        self.assertTrue(result.truncated)
        self.assertIn("line1", result.markdown)
        self.assertIn("line2", result.markdown)
        self.assertNotIn("line3", result.markdown)
        self.assertIn("```", result.markdown)
        self.assertIn("After", result.markdown)

    def test_generate_preview_html_uses_truncated_markdown(self) -> None:
        html, result = generate_preview_html(
            "# Title\n\nVisible\n\nHidden",
            Path("sample.md"),
            PreviewOptions(max_blocks=2),
        )

        self.assertTrue(result.truncated)
        self.assertIn("<title>Title</title>", html)
        self.assertIn("Visible", html)
        self.assertNotIn("Hidden", html)

    def test_invalid_preview_options_raise_value_error(self) -> None:
        with self.assertRaises(ValueError):
            build_markdown_preview("# Title", PreviewOptions(max_blocks=0))

    def test_preview_cli_discovers_markdown_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.md").write_text("# A", encoding="utf-8")
            (root / "b.markdown").write_text("# B", encoding="utf-8")
            (root / "c.html").write_text("<p>C</p>", encoding="utf-8")

            files = discover_input_files([root])

        self.assertEqual([p.name for p in files], ["a.md", "b.markdown"])

    def test_preview_cli_resolves_output_path(self) -> None:
        source = Path("docs/readme.md")

        self.assertEqual(resolve_output_path(source, None), Path("docs/readme.preview.html"))
        self.assertEqual(resolve_output_path(source, Path("out")), Path("out/readme.preview.html"))
        self.assertEqual(resolve_output_path(source, Path("out/custom.html")), Path("out/custom.html"))


if __name__ == "__main__":
    unittest.main()
