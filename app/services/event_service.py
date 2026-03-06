"""Service layer for Event business logic."""

import traceback
from typing import List, Optional

from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup

from app.core.config import settings
from app.models.event import Event
from app.repositories.event_repository import EventRepository
from app.utils.parsers import parse_events
from app.utils.utils import parse_date_range


class EventService:
    """Service for Event business logic and operations."""

    def __init__(self, db):
        """
        Initialize EventService.

        Args:
            db: Async database session
        """
        self.db = db
        self.repository = EventRepository(db)

    async def get_events(
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
        events = await self.repository.get_by_filters(
            start_date=start_date,
            end_date=end_date,
            ranks=ranks,
            types=types,
            groups=groups,
            disciplines=disciplines,
        )

        # Convert empty strings to None for date fields
        for event in events:
            if event.startdate == "":
                event.startdate = None
            if event.enddate == "":
                event.enddate = None

        return events

    async def fetch_and_save_events(
        self,
        start: str = None,
        end: str = None,
        ranks: List[str] = None,
        types: List[str] = None,
        groups: List[str] = None,
        disciplines: List[str] = None,
    ) -> dict:
        """
        Fetch events from external source and save them to database.

        Fetches events from the climbing competition source with specified filters,
        checks for duplicates, and inserts new events into the database.

        Args:
            start: Start date for filtering (format: YYYY-MM-DD)
            end: End date for filtering (format: YYYY-MM-DD)
            ranks: List of competition ranks to filter by
            types: List of event types to filter by
            groups: List of participant groups to filter by
            disciplines: List of disciplines to filter by

        Returns:
            Dictionary with message and number of new events inserted

        Raises:
            Exception: If there's an error during fetching or saving
        """

        try:
            print("Fetching events from source...")
            events = await self.fetch_events_from_source(
                start=start,
                end=end,
                ranks=ranks,
                types=types,
                groups=groups,
                disciplines=disciplines,
            )

            print(f"Found {len(events)} events to save")

            # Check for duplicates and only insert new records
            event_links = [comp["link"] for comp in events]
            print(f"Total event links to check: {len(event_links)}")

            existing_links = await self.repository.get_links_by_batch(event_links)
            print(f"Existing links in DB: {len(existing_links)}")
            print(f"Existing links sample: {list(existing_links)[:5]}")

            new_events = [comp for comp in events if comp["link"] not in existing_links]

            message = f"Found {len(events)} events, {len(new_events)} are new"
            print(f"{message}")
            print(f"Existing links: {len(existing_links)}")
            print(f"New events: {len(new_events)}")

            # Insert events in batches to avoid transaction size limits
            batch_size = 100
            inserted_count = 0

            for i in range(0, len(new_events), batch_size):
                batch = new_events[i : i + batch_size]
                print(f"Processing batch {i//batch_size + 1} with {len(batch)} events")
                try:
                    for new_event in batch:
                        try:
                            if not new_event.get("link"):
                                continue

                            if not new_event.get("date"):
                                continue

                            if not new_event.get("name"):
                                continue

                            if new_event["date"] and new_event["year"]:
                                start_date, end_date = parse_date_range(
                                    new_event["date"], new_event["year"]
                                )
                            else:
                                start_date = None
                                end_date = None

                            event = Event(
                                date=new_event["date"],
                                year=new_event["year"],
                                rank=new_event.get("rank", None),
                                startdate=start_date,
                                enddate=end_date,
                                link=new_event["link"],
                                name=new_event["name"],
                                location=new_event.get("location", ""),
                                type=new_event.get("type", ""),
                                groups=new_event.get("groups", []),
                                disciplines=new_event.get("disciplines", []),
                            )
                            self.db.add(event)
                            inserted_count += 1
                        except Exception as e:
                            print(f"Error inserting event: {e}")
                            continue

                    await self.db.commit()
                    print(
                        f"Successfully committed batch {i//batch_size + 1} with {len(batch)} events"
                    )

                except Exception as e:
                    print(f"Error in batch {i//batch_size + 1}: {e}")
                    traceback.print_exc()
                    await self.db.rollback()
                    continue

            print(f"Successfully inserted total {inserted_count} events")
            return {"message": message, "inserted_count": inserted_count}

        except Exception as e:
            print(f"Error in fetch_and_save_events: {e}")
            traceback.print_exc()
            await self.db.rollback()
            raise

    async def fetch_events_from_source(
        self,
        start: str,
        end: str,
        ranks: List[str] = None,
        types: List[str] = None,
        groups: List[str] = None,
        disciplines: List[str] = None,
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

        def format_param(key: str, values: List[str]) -> dict:
            return {f"{key}[]": values}

        params.update(format_param("ranks", ranks))
        params.update(format_param("types", types))
        params.update(format_param("groups", groups))
        params.update(format_param("disciplines", disciplines))

        try:
            print(f"Making HTTP request to: {base_url}")
            print(f"Parameters: {params}")

            # Build URL manually to see what's being generated

            url_with_params = f"{base_url}?{urlencode(params, doseq=True)}"
            print(f"Full URL: {url_with_params}")

            # Check for invalid characters in URL
            if "?" in url_with_params and url_with_params.count("?") > 1:
                print("ERROR: Multiple '?' in URL")
                return []

            print("Sending HTTP request...")
            print(f"Python version: {__import__('sys').version}")
            print(f"requests version: {requests.__version__}")

            response = requests.get(url_with_params, timeout=10)
            print(f"Response status code: {response.status_code}")

            if response.status_code != 200:
                print(f"Received status code {response.status_code}")
                print(f"Response content (first 500 chars): {response.text[:500]}")
                return []

            response.raise_for_status()
            print("Parsing HTML content...")
            soup = BeautifulSoup(response.content, "html.parser")
            events = parse_events(soup)

            print(f"Parsed {len(events)} events from HTML")
            return events

        except requests.exceptions.RequestException as e:
            print(f"Network error fetching events: {e}")
            return []
        except Exception as e:
            print(f"Error fetching events: {e}")
            return []
