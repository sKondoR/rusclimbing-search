"""Dependency injection definitions."""

from typing import Annotated

from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db.session import get_session
from app.services.event_service import EventService
from app.services.team_service import TeamService

# Database session dependency
SessionDep = Annotated[AsyncSession, Depends(get_session)]

# Event service dependency
EventServiceDep = Annotated[EventService, Depends(EventService)]

# Team service dependency
TeamServiceDep = Annotated[TeamService, Depends(TeamService)]
