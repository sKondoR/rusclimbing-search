"""Event endpoints."""

import traceback
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.core.db.session import get_session
from app.schemas.event import BaseResponse, EventFilter, EventResponse
from app.services.event_service import EventService

eventsRouter = APIRouter(prefix="/api", tags=["events"])


async def get_event_service(db=Depends(get_session)) -> EventService:
    """Dependency for EventService."""
    return EventService(db)


@eventsRouter.get(
    "/events",
    response_model=BaseResponse[List[EventResponse]],
    summary="Get events",
    operation_id="fetch_events",
    description=(
        "Get events from database with optional filtering. "
        "Supports filtering by date range, types, groups, and disciplines."
    ),
)
async def fetch_events(
    filter_: EventFilter = Depends(),
    db: EventService = Depends(get_event_service),
) -> BaseResponse[List[EventResponse]]:
    """
    Get events from database with optional filtering.

    Args:
        filter_: EventFilter object with optional date range, ranks, types, groups, and disciplines
        db: EventService instance

    Returns:
        List of EventResponse objects matching the filter criteria
    """
    try:
        print("fetch_events_remote...")
        events = await db.get_events(
            start_date=filter_.start,
            end_date=filter_.end,
            types=filter_.types,
            groups=filter_.groups,
            disciplines=filter_.disciplines,
        )

        # Convert Event objects to EventResponse
        event_dict_list = []
        for event in events:
            event_dict = event.__dict__.copy()
            if event_dict.get("startdate") == "":
                event_dict["startdate"] = None
            if event_dict.get("enddate") == "":
                event_dict["enddate"] = None
            event_dict_list.append(event_dict)

        event_responses = [
            EventResponse.model_validate(event_dict) for event_dict in event_dict_list
        ]
        event_responses.sort(key=lambda x: x.link)

        return BaseResponse(data=event_responses, success=True)
    except Exception as e:
        error_detail = (
            f"Internal server error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        )
        raise HTTPException(status_code=500, detail=error_detail)


@eventsRouter.get(
    "/events/fetch",
    response_model=BaseResponse,
    summary="Fetch and save events",
    operation_id="fetch_events_remote",
    description=(
        "Fetch events from external source and save them to database. "
        "Fetches events from the climbing competition source with specified "
        "filters, checks for duplicates, and inserts new events into the database."
    ),
)
async def fetch_events_remote(
    filter_: EventFilter = Depends(),
    db: EventService = Depends(get_event_service),
) -> BaseResponse:
    """
    Fetch events from external source and save them to database.

    Fetches events from the climbing competition source with specified filters,
    checks for duplicates, and inserts new events into the database.

    Args:
        filter_: EventFilter object with optional date range, ranks, types, groups, and disciplines
        db: EventService instance

    Returns:
        BaseResponse with message and success status

    Raises:
        HTTPException: If there's an error during fetching or saving
    """
    try:
        print("fetch_events_remote...")
        result = await db.fetch_and_save_events(
            start=filter_.start or "2000-01-01",
            end=filter_.end or "2100-12-31",
            ranks=filter_.ranks or ["Всероссийские", "Международные", "Региональные"],
            types=filter_.types or ["book_competition", "book_festival"],
            groups=filter_.groups
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
            disciplines=filter_.disciplines
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

        return BaseResponse(data=result, success=True, message=result["message"])
    except Exception as e:
        error_detail = (
            f"Internal server error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        )
        raise HTTPException(status_code=500, detail=error_detail)
