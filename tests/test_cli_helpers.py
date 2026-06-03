import tempfile
import unittest
from pathlib import Path

from tests import _paths  # noqa: F401
from a2s.any2html_cli import discover_input_files, resolve_output_path
from a2s.convert_cli import discover_input_files as discover_convert_inputs
from a2s.html2screen_cli import discover_html_files, resolve_output_path as resolve_html_output_path


class CliHelperTests(unittest.TestCase):
    def test_any2html_discovers_markdown_files_in_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            md_file = root / "a.md"
            markdown_file = root / "nested" / "b.markdown"
            ignored_file = root / "c.txt"
            markdown_file.parent.mkdir()
            md_file.write_text("# A", encoding="utf-8")
            markdown_file.write_text("# B", encoding="utf-8")
            ignored_file.write_text("ignore", encoding="utf-8")

            files = discover_input_files([root])

        self.assertEqual([p.name for p in files], ["a.md", "b.markdown"])

    def test_convert_discovers_same_markdown_inputs_as_any2html(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.md").write_text("# A", encoding="utf-8")
            (root / "b.markdown").write_text("# B", encoding="utf-8")
            (root / "c.html").write_text("<p>C</p>", encoding="utf-8")

            files = discover_convert_inputs([root])

        self.assertEqual([p.name for p in files], ["a.md", "b.markdown"])

    def test_html2screen_discovers_html_files_in_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            html_file = root / "a.html"
            nested_html = root / "nested" / "b.html"
            nested_html.parent.mkdir()
            html_file.write_text("<p>A</p>", encoding="utf-8")
            nested_html.write_text("<p>B</p>", encoding="utf-8")
            (root / "c.md").write_text("# C", encoding="utf-8")

            files = discover_html_files([root])

        self.assertEqual([p.name for p in files], ["a.html", "b.html"])

    def test_any2html_resolves_file_and_directory_outputs(self) -> None:
        source = Path("docs/readme.md")

        self.assertEqual(resolve_output_path(source, None), Path("docs/readme.html"))
        self.assertEqual(resolve_output_path(source, Path("out")), Path("out/readme.html"))
        self.assertEqual(resolve_output_path(source, Path("out/custom.html")), Path("out/custom.html"))

    def test_html2screen_output_path_keeps_source_name_in_output_directory(self) -> None:
        source = Path("stage/readme.html")

        self.assertEqual(resolve_html_output_path(source, None), source)
        self.assertEqual(resolve_html_output_path(source, Path("exports")), Path("exports/readme.html"))


if __name__ == "__main__":
    unittest.main()
