import unittest

from tests import _paths  # noqa: F401

try:
    import fastapi  # noqa: F401
except ImportError:
    HAS_FASTAPI = False
else:
    HAS_FASTAPI = True


@unittest.skipIf(not HAS_FASTAPI, "FastAPI dependencies are not installed")
class WebApiTests(unittest.TestCase):
    def test_create_app_registers_api_routes(self) -> None:
        from web import create_app

        app = create_app()
        paths = {route.path for route in app.routes}

        self.assertIn("/", paths)
        self.assertIn("/api/files", paths)
        self.assertIn("/api/health", paths)
        self.assertIn("/api/previews/{file_id}", paths)
        self.assertIn("/api/previews/{file_id}/html", paths)
        self.assertIn("/api/version", paths)
        self.assertEqual(app.title, "Any2Screen API")

    def test_create_app_mounts_static_assets(self) -> None:
        from web import create_app

        app = create_app()
        names = {route.name for route in app.routes}

        self.assertIn("assets", names)

    def test_health_response_shape(self) -> None:
        from web.routes import health

        payload = health().model_dump()

        self.assertEqual(payload["status"], "ok")
        self.assertIn("timestamp", payload)

    def test_version_response_shape(self) -> None:
        from web.routes import version

        payload = version().model_dump()

        self.assertEqual(payload["name"], "any2screen")
        self.assertEqual(payload["api_version"], "0.1.0")
        self.assertIn("upload", payload["capabilities"])
        self.assertIn("preview", payload["capabilities"])

    def test_file_registry_detects_supported_markdown_upload(self) -> None:
        from web.files import FileRegistry

        registry = FileRegistry()
        record = registry.add("report.md", b"# Report")

        self.assertEqual(record.filename, "report.md")
        self.assertEqual(record.size_bytes, 8)
        self.assertEqual(record.extension, ".md")
        self.assertEqual(record.detected_type, "markdown")
        self.assertTrue(record.supported)
        self.assertEqual(record.content, b"# Report")
        self.assertIs(registry.get(record.file_id), record)

    def test_file_registry_marks_unknown_uploads(self) -> None:
        from web.files import FileRegistry

        registry = FileRegistry()
        record = registry.add("archive.zip", b"PK")

        self.assertEqual(record.detected_type, "unknown")
        self.assertFalse(record.supported)

    def test_preview_file_generates_markdown_preview(self) -> None:
        from web.files import file_registry
        from web.routes import preview_file

        record = file_registry.add("report.md", b"# Report\n\nVisible\n\nHidden")
        payload = preview_file(record.file_id, blocks=2).model_dump()

        self.assertEqual(payload["file_id"], record.file_id)
        self.assertEqual(payload["detected_type"], "markdown")
        self.assertTrue(payload["truncated"])
        self.assertIn("<title>Report</title>", payload["html"])
        self.assertIn("Visible", payload["html"])
        self.assertNotIn("Hidden", payload["html"])

    def test_preview_file_generates_text_preview(self) -> None:
        from web.files import file_registry
        from web.routes import preview_file

        record = file_registry.add("notes.txt", b"plain text")
        payload = preview_file(record.file_id).model_dump()

        self.assertEqual(payload["detected_type"], "text")
        self.assertIn("<title>notes</title>", payload["html"])
        self.assertIn("plain text", payload["html"])

    def test_preview_html_returns_html_response(self) -> None:
        from web.files import file_registry
        from web.routes import preview_html

        record = file_registry.add("report.md", b"# Report")
        response = preview_html(record.file_id)

        self.assertEqual(response.media_type, "text/html; charset=utf-8")
        self.assertIn(b"<title>Report</title>", response.body)

    def test_preview_file_rejects_unsupported_type(self) -> None:
        from fastapi import HTTPException
        from web.files import file_registry
        from web.routes import preview_file

        record = file_registry.add("image.png", b"fake")

        with self.assertRaises(HTTPException) as ctx:
            preview_file(record.file_id)

        self.assertEqual(ctx.exception.status_code, 415)


if __name__ == "__main__":
    unittest.main()
