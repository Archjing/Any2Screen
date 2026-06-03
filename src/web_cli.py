#!/usr/bin/env python3
import argparse


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Start the Any2Screen FastAPI development server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python3 scripts/any2screen.py web
  python3 scripts/any2screen.py web --host 0.0.0.0 --port 8080
""",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Bind port (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    args = parser.parse_args()

    try:
        import uvicorn
    except ImportError:
        print("Error: web server requires `fastapi` and `uvicorn`.")
        print("Install dependencies with `uv sync --extra web` or `python3 -m pip install -e '.[web]'`.")
        return 1

    uvicorn.run(
        "web.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
