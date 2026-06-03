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
        self.assertIn("preview", payload["capabilities"])


if __name__ == "__main__":
    unittest.main()
