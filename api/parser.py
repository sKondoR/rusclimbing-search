import re

def parse_events(soup):
    events = []
    
    for link in soup.find_all('a', class_='table__content calendar__link'):
        try:
            # Extract date
            date_span = link.find('p', class_='table__text calendar__date')
            if date_span:
                date = date_span.get_text(strip=True).replace('Даты проведения', '').strip()

            else:
                date = ""
            
            # Extract link
            href = link.get('href', '')
            print(f"href:  {href}")
            
            # Extract name
            name_span = link.find('p', class_='table__text calendar__name')
            name = name_span.get_text(strip=True).replace('Название мероприятия', '').strip() if name_span else ""
            print(f"name:  {name}")
            
            # Extract location
            location_span = link.find('p', class_='table__text calendar__location')
            location = location_span.get_text(strip=True).replace('Локация', '').strip() if location_span else ""
            print(f"location:  {location}")
            
            # Extract type
            type_span = link.find('p', class_='table__text calendar__type')
            type_text = type_span.get_text(strip=True).replace('Тип', '').strip() if type_span else ""
            type_ = type_text
            print(f"type_:  {type_}")
            
            # Extract groups
            groups_span = link.find('p', class_='table__text calendar__group')
            groups = []
            if groups_span:
                groups_text = groups_span.get_text(strip=True).replace('Группы', '').strip()
                groups = [g.strip() for g in groups_text.split(';')]
            print(f"groups:  {groups}")
            
            # Extract disciplines
            disciplines_span = link.find('p', class_='table__text calendar__disciplines')
            disciplines = []
            if disciplines_span:
                disciplines_text = disciplines_span.get_text(strip=True).replace('Дисциплины', '').strip()
                disciplines = [d.strip() for d in disciplines_text.split(';')]
            print(f"disciplines:  {disciplines}")

            # Extract year from link
            year_match = re.search(r'\d{2}', href)
            if year_match:
                year = '20' + year_match.group()
                # Only add year if it's not already in the date
                if not date.endswith(year):
                    date = f"{date} {year}"
            print(f"date:  {date}")
            
            events.append({
                "date": date,
                "link": href,
                "name": name,
                "location": location,
                "type": type_,
                "groups": groups,
                "disciplines": disciplines
            })
            
        except Exception as e:
            print(f"Error parsing event: {e}")
            continue

    return events
