from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ApiModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class HealthResponse(ApiModel):
    status: str
    timestamp: datetime


class VersionResponse(ApiModel):
    name: str
    api_version: str
    capabilities: list[str]
