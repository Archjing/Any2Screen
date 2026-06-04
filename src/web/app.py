from pathlib import Path

from fastapi import FastAPI, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from web.routes import router

STATIC_DIR = Path(__file__).resolve().parent / "static"
ROOT_DIR = Path(__file__).resolve().parents[2]
IMAGE_DIR = ROOT_DIR / "img"


def create_app() -> FastAPI:
    # 创建 FastAPI 应用并挂载 API 路由、静态资源和首页。
    app = FastAPI(
        title="Any2Screen API",
        version="0.1.0",
        description="API-first service for previews, exports, and document conversion.",
    )
    app.include_router(router, prefix="/api")
    app.mount("/assets", StaticFiles(directory=STATIC_DIR), name="assets")
    if IMAGE_DIR.exists():
        app.mount("/img", StaticFiles(directory=IMAGE_DIR), name="img")

    @app.get("/", include_in_schema=False)
    def index() -> FileResponse:
        # 返回 Web shell 首页并禁用缓存。
        return FileResponse(STATIC_DIR / "index.html", headers={"Cache-Control": "no-store"})

    @app.middleware("http")
    async def no_cache_assets(request, call_next):
        # 为前端静态资源响应添加 no-store 缓存控制。
        response: Response = await call_next(request)
        if request.url.path.startswith("/assets/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    return app


app = create_app()
