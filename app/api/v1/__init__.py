"""API v1 routes."""

# Import routers directly from their modules to avoid circular imports
from app.api.v1.endpoints.events import eventsRouter as events
from app.api.v1.endpoints.teams import teamsRouter as teams

__all__ = ["events", "teams"]
