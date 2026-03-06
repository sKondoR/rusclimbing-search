"""Repository for Event data access operations."""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event


class EventRepository:
    """Repository for Event database operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize EventRepository.

        Args:
            db: Async database session
        """
        self.db = db

    async def get_all(self) -> List[Event]:
        """
        Get all events from database.

        Returns:
            List of all Event objects
        """
        result = await self.db.execute(select(Event))
        return list(result.scalars().all())

    async def get_by_filters(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        ranks: Optional[List[str]] = None,
        types: Optional[List[str]] = None,
        groups: Optional[List[str]] = None,
        disciplines: Optional[List[str]] = None,
    ) -> List[Event]:
        """
        Get events with optional filtering.

        Args:
            start_date: Filter events starting after this date
            end_date: Filter events ending before this date
            ranks: Filter events by rank
            types: Filter events by type
            groups: Filter events by groups
            disciplines: Filter events by disciplines

        Returns:
            List of Event objects matching the filter criteria
        """
        print(
            f"get_by_filters called with start_date={start_date}, end_date={end_date}"
        )
        print(
            f"ranks={ranks}, types={types}, groups={groups}, disciplines={disciplines}"
        )

        query = select(Event)

        # Apply date range filter
        if start_date:
            print(f"Applying start_date filter: {start_date}")
            query = query.where(Event.startdate >= start_date)
        if end_date:
            print(f"Applying end_date filter: {end_date}")
            query = query.where(Event.enddate <= end_date)

        # Apply rank filter
        if ranks:
            print(f"Applying ranks filter: {ranks}")
            query = query.where(Event.rank.overlap(ranks))

        # Apply type filter
        if types:
            print(f"Applying types filter: {types}")
            query = query.where(Event.type.in_(types))

        # Apply groups filter
        if groups:
            print(f"Applying groups filter: {groups}")
            query = query.where(Event.groups.overlap(groups))

        # Apply disciplines filter
        if disciplines:
            print(f"Applying disciplines filter: {disciplines}")
            query = query.where(Event.disciplines.overlap(disciplines))

        result = await self.db.execute(query)
        events = list(result.scalars().all())
        print(f"Found {len(events)} events")
        return events

    async def exists_by_link(self, link: str) -> bool:
        """
        Check if an event with the given link exists.

        Args:
            link: Event link to check

        Returns:
            True if event exists, False otherwise
        """
        result = await self.db.execute(
            select(Event.link).where(Event.link == link).limit(1)
        )
        return result.scalar() is not None

    async def get_links_by_batch(self, batch_links: List[str]) -> set:
        """
        Get existing links from a batch of links.

        Args:
            batch_links: List of links to check

        Returns:
            Set of existing links
        """
        result = await self.db.execute(
            select(Event.link).where(Event.link.in_(batch_links))
        )
        return set(link[0] for link in result.fetchall())
