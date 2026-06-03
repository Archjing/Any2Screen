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
        self.assertIs(registry.get(record.file_id), record)

    def test_file_registry_marks_unknown_uploads(self) -> None:
        from web.files import FileRegistry

        registry = FileRegistry()
        record = registry.add("archive.zip", b"PK")

        self.assertEqual(record.detected_type, "unknown")
        self.assertFalse(record.supported)


if __name__ == "__main__":
    unittest.main()
