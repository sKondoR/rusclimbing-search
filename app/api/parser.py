import re
from app.core.config import settings
from app.api.utils import extract_link_id, extract_year_from_link, parse_date_range


def parse_events(soup) -> list:
    """
    Parse HTML content to extract climbing competition events.

    Extracts event information from BeautifulSoup object containing
    competition calendar data.

    Args:
        soup: BeautifulSoup object with HTML content

    Returns:
        List of dictionaries containing parsed event information
    """
    events = []

    for link in soup.find_all("a", class_="table__content calendar__link"):
        try:
            # Extract date
            date_span = link.find("p", class_="table__text calendar__date")
            if date_span:
                date = (
                    date_span.get_text(strip=True)
                    .replace("Даты проведения", "")
                    .strip()
                )
            else:
                date = ""

            # Extract startdate and enddate
            startdate_span = link.find("p", class_="table__text calendar__startdate")
            enddate_span = link.find("p", class_="table__text calendar__enddate")
            
            startdate = ""
            enddate = ""
            
            if startdate_span:
                startdate = startdate_span.get_text(strip=True).strip()
            
            if enddate_span:
                enddate = enddate_span.get_text(strip=True).strip()

            # Extract link
            href = link.get("href", "")
            link_id = extract_link_id(href)

            # Extract name
            name_span = link.find("p", class_="table__text calendar__name")
            name = (
                name_span.get_text(strip=True)
                .replace("Название мероприятия", "")
                .strip()
                if name_span
                else ""
            )

            # Extract location
            location_span = link.find("p", class_="table__text calendar__location")
            location = (
                location_span.get_text(strip=True).replace("Локация", "").strip()
                if location_span
                else ""
            )

            # Filter out events with cancelled status
            if any(rejected_word in location for rejected_word in settings.REJECTED_WORDS):
                continue

            # Extract type
            type_span = link.find("p", class_="table__text calendar__type")
            type_text = (
                type_span.get_text(strip=True).replace("Тип", "").strip()
                if type_span
                else ""
            )
            type_ = type_text

            # Extract groups
            groups_span = link.find("p", class_="table__text calendar__group")
            groups = []
            if groups_span:
                groups_text = (
                    groups_span.get_text(strip=True).replace("Группы", "").strip()
                )
                groups = [g.strip() for g in groups_text.split(";")]

            # Extract disciplines
            disciplines_span = link.find(
                "p", class_="table__text calendar__disciplines"
            )
            disciplines = []
            if disciplines_span:
                disciplines_text = (
                    disciplines_span.get_text(strip=True)
                    .replace("Дисциплины", "")
                    .strip()
                )
                disciplines = [d.strip() for d in disciplines_text.split(";")]

            # Extract year from link (format: 2112kna -> year = `20` + first 2 digits)
            year = extract_year_from_link(href)

            events.append(
                {
                    "date": date,
                    "year": year,
                    "link": link_id,
                    "name": name,
                    "location": location,
                    "type": type_,
                    "groups": groups,
                    "disciplines": disciplines,
                    "startdate": startdate,
                    "enddate": enddate,
                }
            )

        except Exception as e:
            print(f"Error parsing event: {e}")
            continue

    return events

