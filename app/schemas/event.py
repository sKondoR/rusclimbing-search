from datetime import datetime
from typing import Any, Generic, List, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    """Base response model for all API endpoints."""
    success: bool
    data: T | None = None
    message: str | None = None


class EventBase(BaseModel):
    date: str
    link: str
    name: str
    location: str
    type: str
    groups: List[str]
    disciplines: List[str]


class EventCreate(EventBase):
    pass


class EventResponse(EventBase):
    id: int
    created_at: datetime
    updated_at: datetime


class EventFilter(BaseModel):
    start: str | None = None
    end: str | None = None
    ranks: List[str] | None = None
    types: List[str] | None = None
    groups: List[str] | None = None
    disciplines: List[str] | None = None
