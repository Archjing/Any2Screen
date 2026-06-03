import unittest
from pathlib import Path

from tests import _paths  # noqa: F401
from a2s.any2html.markdown import (
    convert_md_to_html,
    detect_lang,
    extract_title,
    generate_html,
    wrap_tables,
)


class MarkdownConversionTests(unittest.TestCase):
    def test_generate_html_wraps_document_with_title_and_source(self) -> None:
        html = generate_html("# Report\n\nHello **Any2Screen**.", Path("report.md"))

        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("<html lang=\"en\">", html)
        self.assertIn("<title>Report</title>", html)
        self.assertIn("<strong>Any2Screen</strong>", html)
        self.assertIn("report.md", html)

    def test_generate_html_escapes_title_and_source_filename(self) -> None:
        html = generate_html("# A <B>", Path("source<&>.md"))

        self.assertIn("<title>A &lt;B&gt;</title>", html)
        self.assertIn("source&lt;&amp;&gt;.md", html)

    def test_extract_title_falls_back_to_filename_stem(self) -> None:
        title = extract_title("## Subtitle only\n\nBody", Path("notes.md"))

        self.assertEqual(title, "notes")

    def test_detect_lang_marks_chinese_documents(self) -> None:
        lang = detect_lang("这是一个中文文档，用来测试语言检测。\n\nHello")

        self.assertEqual(lang, "zh-CN")

    def test_convert_md_to_html_wraps_tables(self) -> None:
        markdown = "| A | B |\n|---|---|\n| 1 | 2 |\n"
        html = convert_md_to_html(markdown)

        self.assertIn('<div class="table-wrapper">', html)
        self.assertIn("<table>", html)

    def test_wrap_tables_marks_tall_tables(self) -> None:
        rows = "".join("<tr><td>row</td></tr>" for _ in range(16))
        html = wrap_tables(f"<table>{rows}</table>")

        self.assertIn('<div class="table-wrapper tall">', html)


if __name__ == "__main__":
    unittest.main()
