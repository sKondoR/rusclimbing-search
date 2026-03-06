"""Repository for TeamCache data access operations."""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.team import TeamCache


class TeamRepository:
    """Repository for TeamCache database operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize TeamRepository.

        Args:
            db: Async database session
        """
        self.db = db

    async def get_by_year(self, year: str) -> Optional[TeamCache]:
        """
        Get team cache entry for a specific year.

        Args:
            year: Competition year

        Returns:
            TeamCache object if found, None otherwise
        """
        result = await self.db.execute(
            select(TeamCache).where(TeamCache.year == year).limit(1)
        )
        return result.scalar_one_or_none()

    async def save_teams(self, year: str, teams: List[str]) -> TeamCache:
        """
        Save or update team cache entry.

        Args:
            year: Competition year
            teams: List of team names

        Returns:
            TeamCache object that was saved/updated
        """
        # Check if entry exists
        existing = await self.get_by_year(year)

        if existing:
            # Update existing entry
            existing.teams = teams
            return existing

        # Create new entry
        cache_entry = TeamCache(year=year, teams=teams)
        self.db.add(cache_entry)
        return cache_entry

    async def get_all_years(self) -> List[str]:
        """
        Get all years that have cached team data.

        Returns:
            List of years with cached data
        """
        result = await self.db.execute(select(TeamCache.year))
        return list(result.scalars().all())
