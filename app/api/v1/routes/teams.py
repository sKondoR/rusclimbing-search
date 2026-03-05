from typing import List

import traceback
import requests
from bs4 import BeautifulSoup
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.db.session import get_session
from app.models.event import Event
from app.models.team import TeamCache
from app.core.config import settings

teamsRouter = APIRouter(prefix="/api", tags=["teams"])

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
    dependencies=[], # Depends(PermissionCheck())
)
async def get_teams(db: AsyncSession = Depends(get_session)):
    # First, try to get teams from cache
    cache_query = select(TeamCache).where(TeamCache.year == str(settings.EVENT_YEAR))
    cache_result = await db.execute(cache_query)
    cached_teams = cache_result.scalars().first()

    # If cache exists, return cached data
    if cached_teams:
        return {"teams": cached_teams.teams, "event": settings.EVENT_NAME, "link": settings.EVENT_YEAR, "from_cache": True}

    # Find the event with name EVENT_NAME and year EVENT_YEAR in groups [EVENT_GROUP]
    query = select(Event).where(Event.name == settings.EVENT_NAME).where(Event.year == settings.EVENT_YEAR)
    result = await db.execute(query)
    events = result.scalars().all()

    # Filter events by group EVENT_GROUP
    filtered_events = [event for event in events if settings.EVENT_GROUP in event.groups]
    # print(f"Filtered events by group '{settings.EVENT_GROUP}': {len(filtered_events)} events found")
    # for idx, event in enumerate(filtered_events):
    #     print(f"  Match {idx}: name='{event.name}', link='{event.link}', year='{event.year}', groups={event.groups}")

    if not filtered_events:
        raise HTTPException(status_code=404, detail=f"Event '{settings.EVENT_NAME}' with group '{settings.EVENT_GROUP}' and year {settings.EVENT_YEAR} not found")

    # Take the first matching event
    event = filtered_events[0]

    # Construct the URL for live results
    url = f"{settings.LIVE_RESULTS_BASE_URL}{event.link}/{settings.LIVE_RESULTS_PATH}"

    # print(f"url: {url}")
    try:
        # Make GET request to the live results page
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Parse the HTML content
        soup = BeautifulSoup(response.content, "html.parser")

        # Find all td elements with class "Команда" (Team)
        team_elements = soup.find_all("td", class_="command")

        # Extract text from each element, create a set of unique teams, and sort alphabetically
        teams = sorted(set(elem.get_text(strip=True) for elem in team_elements))

        # Save teams to cache
        cache_entry = TeamCache(year=str(settings.EVENT_YEAR), teams=teams)
        db.add(cache_entry)
        await db.commit()

        return {"teams": teams, "event": event.name, "link": event.link, "from_cache": False}

    except requests.exceptions.RequestException as e:
        print(f"Network error fetching live results: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch live results: {str(e)}")
    except Exception as e:
        print(f"Error parsing live results: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to parse live results: {str(e)}")