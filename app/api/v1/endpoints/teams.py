"""Team endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_session
from app.services.team_service import TeamService

teamsRouter = APIRouter(prefix="/api", tags=["teams"])


async def get_team_service(db: AsyncSession = Depends(get_session)) -> TeamService:
    """Dependency for TeamService."""
    return TeamService(db)


@teamsRouter.get(
    "/teams",
    summary="Get teams",
    operation_id="get_teams",
    description=(
        "Get teams from the specified event by parsing the live results page. "
        "Finds the event 'Первенство России' with year 2025 and group 'Ю', "
        "then fetches and parses the live results page to extract team names. "
        "Returns cached data if available for the specified year."
    ),
)
async def get_teams(
    db: TeamService = Depends(get_team_service),
):
    """
    Get teams from the specified event.

    Args:
        db: TeamService instance

    Returns:
        Dictionary containing teams, event info, and cache status

    Raises:
        HTTPException: If there's an error during fetching or parsing
    """
    try:
        return await db.get_teams()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get teams: {str(e)}")
