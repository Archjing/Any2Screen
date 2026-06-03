from fastapi import FastAPI

from web.routes import router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Any2Screen API",
        version="0.1.0",
        description="API-first service for previews, exports, and document conversion.",
    )
    app.include_router(router, prefix="/api")
    return app


app = create_app()
