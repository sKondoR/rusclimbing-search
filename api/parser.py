import re

def parse_competitions(soup):
    competitions = []
    
    for link in soup.find_all('a', class_='table__content calendar__link'):
        try:
            # Extract date
            date_span = link.find('p', class_='table__text calendar__date')
            if date_span:
                date_text = date_span.get_text(strip=True)
                # More flexible date pattern matching
                date_match = re.search(r'\d{1,2}\s*[-–]\s*\d{1,2}\s*(?:\w+)?', date_text)
                if date_match:
                    date = date_match.group()
                else:
                    # Fallback to just the text if no match
                    date = date_text
            else:
                date = ""
            
            # Extract link
            href = link.get('href', '')
            print(f"href:  {href}")
            
            # Extract name
            name_span = link.find('p', class_='table__text calendar__name')
            name = ''.join(name_span.find_all(text=True, recursive=False)) if name_span else ""
            print(f"name:  {name}")
            
            # Extract location
            location_span = link.find('p', class_='table__text calendar__location')
            location = ''.join(location_span.find_all(text=True, recursive=False)) if location_span else ""
            print(f"location:  {location}")
            
            # Extract type
            type_span = link.find('p', class_='table__text calendar__type')
            type_text = ''.join(type_span.find_all(text=True, recursive=False)) if type_span else ""
            type_match = re.search(r'[А-Яа-я]+', type_text)
            type_ = type_match.group() if type_match else ""
            print(f"type_:  {type_}")
            
            # Extract groups
            groups_span = link.find('p', class_='table__text calendar__group')
            groups = []
            if groups_span:
                groups_text = ''.join(groups_span.find_all(text=True, recursive=False))
                groups = [g.strip() for g in re.findall(r'[А-Яа-я]+', groups_text)]
            print(f"groups:  {groups}")
            
            # Extract disciplines
            disciplines_span = link.find('p', class_='table__text calendar__disciplines')
            disciplines = []
            if disciplines_span:
                disciplines_text = ''.join(disciplines_span.find_all(text=True, recursive=False))
                disciplines = [d.strip() for d in re.findall(r'[А-Яа-я]+', disciplines_text)]
            print(f"disciplines:  {disciplines}")

            # Extract year from link
            year_match = re.search(r'\d{2}', href)
            if year_match:
                year = '20' + year_match.group()
                date = f"{date} {year}"
            print(f"date:  {date}")
            
            competitions.append({
                "date": date,
                "link": href,
                "name": name,
                "location": location,
                "type": type_,
                "groups": groups,
                "disciplines": disciplines
            })
            
        except Exception as e:
            print(f"Error parsing competition: {e}")
            continue

    return competitions
