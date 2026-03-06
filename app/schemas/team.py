from datetime import datetime
from typing import Generic, List, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    """Base response model for all API endpoints."""

    success: bool
    data: T | None = None
    message: str | None = None


class TeamBase(BaseModel):
    year: str
    teams: List[str]


class TeamCreate(TeamBase):
    pass


class TeamResponse(TeamBase):
    id: int
    created_at: datetime
    updated_at: datetime
