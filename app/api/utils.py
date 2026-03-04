import re
from datetime import datetime
from typing import Union, Optional, Tuple

def extract_link_id(href: str) -> Union[str, None]:
    """
    Извлекает ID из ссылки на соревнование.
    
    Args:
        href: URL-адрес ссылки
        
    Returns:
        ID ссылки или None, если не удалось извлечь
    """
    if not href:
        return None
    
    if href.startswith("/competitions/") and href.endswith("/"):
        href = href[14:-1]  # Убираем "/competitions/" (14 символов) и "/"
    
    return href

def extract_year_from_link(href: str) -> str:
    """
    Извлекает год из ссылки.
    
    Args:
        href: URL-адрес ссылки
        
    Returns:
        Год в формате YYYY или пустая строка, если не удалось извлечь
    """
    if not href:
        return ""
    
    # Ищем первые 2 цифры в ссылке
    year_match = re.search(r"\d{2}", href)
    if year_match:
        year_str = year_match.group(0)
        # Проверяем, что это валидный год (2000-2099)
        year_num = int(year_str)
        if 0 <= year_num <= 99:
            return f"20{year_str}"
    return ""

def parse_date_range(date_str: str, year: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Распарсить диапазон дат в формат YYYY-MM-DD.
    
    Args:
        date_str: Дата в одном или двух форматах
        year: год в формате YYYY (может быть пустой строкой)
        
    Returns:
        Кортежная дата начала и конца диапазона (обе или оба)
    """
    if not date_str:
        return None, None
    
    # Карта месяцев
    month_map = {
        "января": "01", "февраля": "02", "марта": "03",
        "апреля": "04", "мая": "05", "июня": "06",
        "июля": "07", "августа": "08", "сентября": "09",
        "октября": "10", "ноября": "11", "декабря": "12"
    }
    
    # Проверяем, есть ли явный год в строке
    has_explicit_year = any(len(part) == 4 and part.isdigit() for part in date_str.split())
    
    # Ищем диапазон (дефис между датами) - делаем это ДО замены символов
    if "-" in date_str or "—" in date_str:
        # Разделяем на две части
        if "-" in date_str:
            date_parts = date_str.split("-", 1)
        else:
            date_parts = date_str.split("—", 1)
        
        # Удаляем лишние символы и пробелы из частей
        start_str = date_parts[0].strip().lower().replace("/", " ").replace(",", " ")
        end_str = date_parts[1].strip().lower().replace("/", " ").replace(",", " ")
        
        # Парсим обе даты
        start_date = _parse_single_date(start_str, year, month_map, has_explicit_year)
        end_date = _parse_single_date(end_str, year, month_map, has_explicit_year)
        
        # Если первый месяц пропущен, используем месяц из второй даты
        if start_date and end_date and start_date[5:7] == "01" and end_date[5:7] != "01":
            start_date = start_date[:5] + end_date[5:7] + start_date[7:]
        
        return start_date, end_date
    
    # Если нет диапазона - парсим одну дату и возвращаем её дважды
    single_date = _parse_single_date(date_str, year, month_map, has_explicit_year)
    return single_date, single_date

def _parse_single_date(date_str: str, year: str, month_map: dict, has_explicit_year: bool) -> Optional[str]:
    """
    Проанализировать одну дату.
    Возвращает дату в формате YYYY-MM-DD или None.
    """
    if not date_str:
        return None
    
    # Удаляем лишние символы
    date_str = date_str.strip().lower().replace("/", " ").replace(",", " ")
    
    # Ищем месяц
    month = None
    for month_name, month_num in month_map.items():
        if month_name in date_str:
            month = month_num
            break
    
    # Ищем год
    date_year = year or "2026"  # По умолчанию используем 2026
    if has_explicit_year:
        # Ищем явный год в строке
        year_match = re.search(r"\b(20\d{2})\b", date_str)
        if year_match:
            date_year = year_match.group(1)
    
    # Ищем день
    day = None
    # Сначала ищем числа в формате "день месяц"
    if month:
        # Ищем число перед месяцем
        parts = date_str.split(month_name, 1)
        if parts[0].strip():
            # Ищем число в первой части
            day_match = re.search(r"(\d{1,2})", parts[0])
            if day_match:
                day = day_match.group(1).zfill(2)
    
    # Если день не найден, ищем любое число
    if not day:
        day_match = re.search(r"(\d{1,2})", date_str)
        if day_match:
            day = day_match.group(1).zfill(2)
    
    # Обрабатываем особые случаи
    if month and not day:
        # Только месяц - используем 1-е число
        return f"{date_year}-{month}-01"
    
    if day and not month:
        # Только день - используем январь
        return f"{date_year}-01-{day}"
    
    if day and month:
        return f"{date_year}-{month}-{day}"
    
    return None

def _parse_single_date(date_str: str, year: str, month_map: dict, has_explicit_year: bool) -> Optional[str]:
    """
    Проанализировать одну дату.
    Возвращает дату в формате YYYY-MM-DD или None.
    """
    if not date_str:
        return None
    
    # Удаляем лишние символы
    date_str = date_str.strip().lower().replace("/", " ").replace(",", " ")
    
    # Ищем месяц
    month = None
    for month_name, month_num in month_map.items():
        if month_name in date_str:
            month = month_num
            break
    
    # Ищем год
    date_year = year or "2026"  # По умолчанию используем 2026
    if has_explicit_year:
        # Ищем явный год в строке
        year_match = re.search(r"\b(20\d{2})\b", date_str)
        if year_match:
            date_year = year_match.group(1)
    
    # Ищем день
    day = None
    # Сначала ищем числа в формате "день месяц"
    if month:
        # Ищем число перед месяцем
        parts = date_str.split(month_name, 1)
        if parts[0].strip():
            # Ищем число в первой части
            day_match = re.search(r"(\d{1,2})", parts[0])
            if day_match:
                day = day_match.group(1).zfill(2)
    
    # Если день не найден, ищем любое число
    if not day:
        day_match = re.search(r"(\d{1,2})", date_str)
        if day_match:
            day = day_match.group(1).zfill(2)
    
    # Обрабатываем особые случаи
    if month and not day:
        # Только месяц - используем 1-е число
        return f"{date_year}-{month}-01"
    
    if day and not month:
        # Только день - используем январь
        return f"{date_year}-01-{day}"
    
    if day and month:
        return f"{date_year}-{month}-{day}"
    
    return None

# Добавляем отладку для отладки
