from pydantic import BaseModel
from typing import List
from datetime import datetime

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