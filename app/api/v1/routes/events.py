from app.core.config import settings

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
import requests

from app.schemas.event import EventResponse, EventFilter
from app.api.db import get_db
from app.api.models import Event
from app.api.parser import parse_events
from bs4 import BeautifulSoup

router = APIRouter(prefix="/api", tags=["events"])

@router.get("/events", response_model=List[EventResponse])
async def get_events(
    filter: EventFilter = Depends(),
    db: AsyncSession = Depends(get_db)
):
    query = select(Event)
    
    if filter.start:
        query = query.where(Event.date >= filter.start)
    if filter.end:
        query = query.where(Event.date <= filter.end)
    if filter.ranks:
        # Note: ranks are not stored in the database, they are used for filtering at source
        pass
    if filter.types:
        query = query.where(Event.type.in_(filter.types))
    if filter.groups:
        query = query.where(Event.groups.overlap(filter.groups))
    if filter.disciplines:
        query = query.where(Event.disciplines.overlap(filter.disciplines))
    
    result = await db.execute(query)
    events = result.scalars().all()
    
    return events

@router.get("/events/fetch", response_model=List[EventResponse])
async def fetch_and_save_events(
    filter: EventFilter = Depends(),
    db: AsyncSession = Depends(get_db)
):
    try:
        events = await fetch_events_from_source(
            filter.start or "2000-01-01",
            filter.end or "2100-12-31",
            filter.ranks or ["Всероссийские", "Международные", "Региональные"],
            filter.types or ["book_competition", "book_festival"],
            filter.groups or ["adults", "juniors", "teenagers", "younger", "v10", "v13", "v15", "v19"],
            filter.disciplines or ["bouldering", "dvoerobye", "etalon", "skorost", "trudnost", "sv", "mnogobore"]
        )
        
        # Log how many events were found
        print(f"Found {len(events)} events to save")
        
        # Check for duplicates and only insert new records
        # Get existing links for the current batch
        existing_links = set()
        batch_links = [comp["link"] for comp in events]
        
        # Check which links already exist in DB
        try:
            result = await db.execute(select(Event.link).where(Event.link.in_(batch_links)))
            existing_links = set(link[0] for link in result.fetchall())
        except Exception as e:
            print(f"Error checking existing links: {e}")
            # If we can't check existing links, proceed with all events
            existing_links = set()
        
        # Filter out duplicates and insert only new records
        new_events = [comp for comp in events if comp["link"] not in existing_links]
        
        print(f"Found {len(events)} events, {len(new_events)} are new")
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
                    disciplines=comp["disciplines"]
                )
                db.add(event)
                inserted_count += 1
            except Exception as e:
                print(f"Error inserting event with link {comp['link']}: {e}")
                continue
        
        print(f"Successfully inserted {inserted_count} events")
        await db.commit()
        
        return await get_events(filter, db)
    except Exception as e:
        print(f"Error in fetch_and_save_events: {e}")
        # Log the full traceback for debugging
        import traceback
        traceback.print_exc()
        # Rollback in case of error
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

async def fetch_events_from_source(start: str, end: str, ranks: List[str], types: List[str], groups: List[str], disciplines: List[str]):
    base_url = settings.BASE_URL
    
    params = {
        "start": start,
        "end": end,
    }
    
    # Convert parameters to URL format
    def format_param(key, values):
        return {f"{key}[]": values}
    
    params.update(format_param("ranks", ranks))
    params.update(format_param("types", types))
    params.update(format_param("groups", groups))
    params.update(format_param("disciplines", disciplines))
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        events = parse_events(soup)
        
        return events
        
    except requests.exceptions.RequestException as e:
        print(f"Network error fetching events: {e}")
        return []
    except Exception as e:
        print(f"Error fetching events: {e}")
        return []
