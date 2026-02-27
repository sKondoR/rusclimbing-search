from typing import List

import traceback
import requests
from bs4 import BeautifulSoup
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.db import get_db
from app.api.models import Event
from app.api.parser import parse_events
from app.core.config import settings
# from app.core.permissions import PermissionCheck
from app.schemas.event import BaseResponse, EventFilter, EventResponse

router = APIRouter(prefix="/api", tags=["events"])


@router.get(
    "/events",
    response_model=BaseResponse[List[EventResponse]],
    summary="Get events",
    operation_id="get_events",
    description=(
        "Get events from database with optional filtering. "
        "Supports filtering by date range, types, groups, and disciplines."
    ),
    dependencies=[], # Depends(PermissionCheck())
)
async def get_events(
    filter_: EventFilter = Depends(), db: AsyncSession = Depends(get_db)
) -> BaseResponse[List[EventResponse]]:
    """
    Get events from database with optional filtering.

    Args:
        filter_: EventFilter object with optional date range, ranks, types, groups, and disciplines
        db: Async database session

    Returns:
        List of EventResponse objects matching the filter criteria
    """
    query = select(Event)

    if filter_.start:
        query = query.where(Event.date >= filter_.start)
    if filter_.end:
        query = query.where(Event.date <= filter_.end)
    if filter_.ranks:
        # Note: ranks are not stored in the database, they are used for filtering at source
        pass
    if filter_.types:
        query = query.where(Event.type.in_(filter_.types))
    if filter_.groups:
        query = query.where(Event.groups.overlap(filter_.groups))
    if filter_.disciplines:
        query = query.where(Event.disciplines.overlap(filter_.disciplines))

    result = await db.execute(query)
    events = result.scalars().all()

    # Convert Event objects to EventResponse
    event_responses = [EventResponse.model_validate(event.__dict__) for event in events]
    return BaseResponse(data=event_responses, success=True)


@router.get(
    "/events/fetch",
    response_model=BaseResponse,
    summary="Fetch and save events",
    operation_id="fetch_and_save_events",
    description=(
        "Fetch events from external source and save them to database. "
        "Fetches events from the climbing competition source with specified "
        "filters, checks for duplicates, and inserts new events into the database."
    ),
    dependencies=[],
)
async def fetch_and_save_events(
    filter_: EventFilter = Depends(), db: AsyncSession = Depends(get_db)
) -> List[EventResponse]:
    """
    Fetch events from external source and save them to database.

    Fetches events from the climbing competition source with specified filters,
    checks for duplicates, and inserts new events into the database.

    Args:
        filter_: EventFilter object with optional date range, ranks, types, groups, and disciplines
        db: Async database session

    Returns:
        List of Event objects after saving

    Raises:
        HTTPException: If there's an error during fetching or saving
    """
    try:
        events = await fetch_events_from_source(
            filter_.start or "2000-01-01",
            filter_.end or "2100-12-31",
            filter_.ranks or ["Всероссийские", "Международные", "Региональные"],
            filter_.types or ["book_competition", "book_festival"],
            filter_.groups
            or [
                "adults",
                "juniors",
                "teenagers",
                "younger",
                "v10",
                "v13",
                "v15",
                "v19",
            ],
            filter_.disciplines
            or [
                "bouldering",
                "dvoerobye",
                "etalon",
                "skorost",
                "trudnost",
                "sv",
                "mnogobore",
            ],
        )

        # Log how many events were found
        print(f"Found {len(events)} events to save")

        # Check for duplicates and only insert new records
        # Get existing links for the current batch
        existing_links = set()
        batch_links = [comp["link"] for comp in events]

        # Check which links already exist in DB
        try:
            result = await db.execute(
                select(Event.link).where(Event.link.in_(batch_links))
            )
            existing_links = set(link[0] for link in result.fetchall())
        except Exception as e:
            print(f"Error checking existing links: {e}")
            # If we can't check existing links, proceed with all events
            existing_links = set()

        # Filter out duplicates and insert only new records
        new_events = [comp for comp in events if comp["link"] not in existing_links]

        message = f"Found {len(events)} events, {len(new_events)} are new"
        print(message)
        print(f"Existing links: {len(existing_links)}")

        inserted_count = 0
        for comp in new_events:
            try:
                event = Event(
                    date=comp["date"],
                    link=comp["link"],
                    name=comp["name"],
                    location=comp["location"],
                    type=comp["type"],
                    groups=comp["groups"],
                    disciplines=comp["disciplines"],
                )
                db.add(event)
                inserted_count += 1
            except Exception as e:
                print(f"Error inserting event with link {comp['link']}: {e}")
                continue

        print(f"Successfully inserted {inserted_count} events")
        await db.commit()
        # await get_events(filter_, db)
        # Return the updated events list
        return BaseResponse(data=new_events, success=True, message=message )
    except Exception as e:
        print(f"Error in fetch_and_save_events: {e}")
        traceback.print_exc()
        # Rollback in case of error
        await db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}"
        ) from e


async def fetch_events_from_source(
    start: str,
    end: str,
    ranks: List[str],
    types: List[str],
    groups: List[str],
    disciplines: List[str],
) -> List[dict]:
    """
    Fetch events from external climbing competition source.

    Makes HTTP request to the competition source API with specified filters
    and parses the response to extract event information.

    Args:
        start: Start date for filtering (format: YYYY-MM-DD)
        end: End date for filtering (format: YYYY-MM-DD)
        ranks: List of competition ranks to filter by
        types: List of event types to filter by
        groups: List of participant groups to filter by
        disciplines: List of disciplines to filter by

    Returns:
        List of dictionaries containing event information

    Raises:
        requests.exceptions.RequestException: If network request fails
    """
    base_url = settings.BASE_URL

    params = {
        "start": start,
        "end": end,
    }

    # Convert parameters to URL format
    def format_param(key: str, values: List[str]) -> dict:
        """
        Format parameter for URL query string.

        Args:
            key: Parameter name
            values: List of values for the parameter

        Returns:
            Dictionary with formatted parameter key and values
        """
        return {f"{key}[]": values}

    params.update(format_param("ranks", ranks))
    params.update(format_param("types", types))
    params.update(format_param("groups", groups))
    params.update(format_param("disciplines", disciplines))

    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        events = parse_events(soup)

        return events

    except requests.exceptions.RequestException as e:
        print(f"Network error fetching events: {e}")
        return []
    except Exception as e:
        print(f"Error fetching events: {e}")
        return []
