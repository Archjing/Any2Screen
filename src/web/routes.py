from datetime import datetime, timezone

from fastapi import APIRouter

from web.schemas import HealthResponse, VersionResponse


router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    return HealthResponse(status="ok", timestamp=datetime.now(timezone.utc))


@router.get("/version", response_model=VersionResponse, tags=["system"])
def version() -> VersionResponse:
    return VersionResponse(
        name="any2screen",
        api_version="0.1.0",
        capabilities=["preview", "convert", "export"],
    )
