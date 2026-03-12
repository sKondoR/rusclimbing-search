"""Service layer for Team business logic."""

import traceback

import requests
from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.event import Event
from app.repositories.team_repository import TeamRepository


class TeamService:
    """Service for Team business logic and operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize TeamService.

        Args:
            db: Async database session
        """
        self.db = db
        self.repository = TeamRepository(db)

    async def get_teams(self) -> dict:
        """
        Get teams from the specified event by parsing the live results page.

        Finds the event 'Первенство России' with year 2025 and group 'Ю',
        then fetches and parses the live results page to extract team names.
        Returns cached data if available for the specified year.
        Returns empty teams list if external site is unavailable.

        Returns:
            Dictionary containing teams, event info, and cache status

        Raises:
            Exception: If there's an error during fetching or parsing
        """
        try:
            # First, try to get teams from cache
            cached_teams = await self.repository.get_by_year(str(settings.EVENT_YEAR))
            # If cache exists, return cached data
            if cached_teams:
                return {
                    "teams": cached_teams.teams,
                    "event": settings.EVENT_NAME,
                    "link": str(settings.EVENT_YEAR),
                    "from_cache": True,
                }

            # Find the event with name EVENT_NAME and year EVENT_YEAR
            events = await self.db.execute(
                select(Event).where(
                    Event.name == settings.EVENT_NAME,
                    Event.year == settings.EVENT_YEAR,
                )
            )
            events_list = events.scalars().all()

            # Filter events by group EVENT_GROUP
            filtered_events = [
                event for event in events_list if settings.EVENT_GROUP in event.groups
            ]

            if not filtered_events:
                raise Exception(
                    f"Event '{settings.EVENT_NAME}' with group '{settings.EVENT_GROUP}' "
                    f"and year {settings.EVENT_YEAR} not found"
                )

            # Take the first matching event
            event = filtered_events[0]

            # Construct the URL for live results
            url = f"{settings.LIVE_RESULTS_BASE_URL}{event.link}/{settings.LIVE_RESULTS_PATH}"

            # Make GET request to the live results page
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Parse the HTML content
            soup = BeautifulSoup(response.content, "html.parser")

            # Find all td elements with class "Команда" (Team)
            team_elements = soup.find_all("td", class_="command")

            # Extract text from each element, create a set of unique teams, and sort alphabetically
            teams = sorted(set(elem.get_text(strip=True) for elem in team_elements))

            # Save teams to cache
            await self.repository.save_teams(str(settings.EVENT_YEAR), teams)

            return {
                "teams": teams,
                "event": event.name,
                "link": event.link,
                "from_cache": False,
            }

        except requests.exceptions.Timeout:
            print(f"Timeout fetching live results from {settings.LIVE_RESULTS_BASE_URL}")
            # Return empty list instead of raising exception
            return {
                "teams": [],
                "event": settings.EVENT_NAME,
                "link": str(settings.EVENT_YEAR),
                "from_cache": False,
                "error": "External site timeout, no teams available"
            }
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error fetching live results: {e}")
            # Return empty list instead of raising exception
            return {
                "teams": [],
                "event": settings.EVENT_NAME,
                "link": str(settings.EVENT_YEAR),
                "from_cache": False,
                "error": "External site connection error, no teams available"
            }
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching live results: {e}")
            # Return empty list instead of raising exception
            return {
                "teams": [],
                "event": settings.EVENT_NAME,
                "link": str(settings.EVENT_YEAR),
                "from_cache": False,
                "error": f"Failed to fetch live results: {str(e)}"
            }
        except Exception as e:
            print(f"Error parsing live results: {e}")
            traceback.print_exc()
            raise Exception(f"Failed to parse live results: {str(e)}")
