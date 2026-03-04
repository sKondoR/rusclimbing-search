import unittest
from bs4 import BeautifulSoup
from app.api.parser import parse_events
from app.api.utils import parse_date_range


class TestParseEvents(unittest.TestCase):
    """
    Unit tests for parse_events function.

    Tests parsing of HTML content containing climbing competition events.
    """

    def test_parse_events(self):
        """
        Test parsing of competition events from HTML.

        Verifies that the parse_events function correctly extracts
        event information including date, link, name, location, type,
        groups, and disciplines from HTML content.
        """
        # Mock HTML content
        html_content = """
        <li class="table__item" data-accordion="element">
            <a class="table__content calendar__link" data-accordion="content" href="/competitions/2103voronezh_ch/">
                <p class="table__text calendar__date"><span>Даты проведения</span>04 - 07 марта</p>
                <p class="table__text calendar__name"><span>Название мероприятия</span>Чемпионат России</p>
                <p class="calendar__button calendar__button--up" data-accordion="button">Развернуть</p>
                <p class="table__text calendar__type"><span>Тип</span>С</p>
                <p class="table__text calendar__group">
                    <span>Группы</span>
                    В
                </p>
                <p class="table__text calendar__disciplines">
                    <span>Дисциплины</span>
                    Б
                </p>
                <p class="table__text calendar__location"><span>Локация</span>Воронеж</p>
                <p class="calendar__button" data-accordion="button">Свернуть</p>
            </a>
        </li>
        <li class="table__item" data-accordion="element">
            <a class="table__content calendar__link" data-accordion="content" href="/competitions/2403msk_vs1/">
                <p class="table__text calendar__date"><span>Даты проведения</span>31 марта - 05 апреля</p>
                <p class="table__text calendar__name"><span>Название мероприятия</span>Всероссийские соревнования</p>
                <p class="calendar__button calendar__button--up" data-accordion="button">Развернуть</p>
                <p class="table__text calendar__type"><span>Тип</span>С</p>
                <p class="table__text calendar__group">
                    <span>Группы</span>
                    Ю; С                            </p>
                <p class="table__text calendar__disciplines">
                    <span>Дисциплины</span>
                    Т; Эт                            </p>
                <p class="table__text calendar__location"><span>Локация</span>Москва</p>
                <p class="calendar__button" data-accordion="button">Свернуть</p>
            </a>
        </li>
        """

        # Create BeautifulSoup object
        soup = BeautifulSoup(html_content, "html.parser")

        # Call the function
        result = parse_events(soup)

        # Assert the result
        self.assertEqual(len(result), 2)

        event = result[0]
        self.assertEqual(event["date"], "04 - 07 марта")
        self.assertEqual(event["year"], "2021")
        self.assertEqual(event["link"], "2103voronezh_ch")
        self.assertEqual(event["name"], "Чемпионат России")
        self.assertEqual(event["location"], "Воронеж")
        self.assertEqual(event["type"], "С")
        self.assertEqual(event["groups"], ["В"])
        self.assertEqual(event["disciplines"], ["Б"])

        event2 = result[1]
        self.assertEqual(event2["date"], "31 марта - 05 апреля")
        self.assertEqual(event2["year"], "2024")
        self.assertEqual(event2["link"], "2403msk_vs1")
        self.assertEqual(event2["name"], "Всероссийские соревнования")
        self.assertEqual(event2["location"], "Москва")
        self.assertEqual(event2["type"], "С")
        self.assertEqual(event2["groups"], ["Ю", "С"])
        self.assertEqual(event2["disciplines"], ["Т", "Эт"])
        
        # Test with link that doesn't contain year
        html_no_year = """
        <li class="table__item" data-accordion="element">
            <a class="table__content calendar__link" data-accordion="content" href="/competitions/no_year/">
                <p class="table__text calendar__date"><span>Даты проведения</span>01 января</p>
                <p class="table__text calendar__name"><span>Название мероприятия</span>Тест</p>
                <p class="table__text calendar__location"><span>Локация</span>Москва</p>
                <p class="table__text calendar__type"><span>Тип</span>С</p>
            </a>
        </li>
        """
        soup_no_year = BeautifulSoup(html_no_year, "html.parser")
        result_no_year = parse_events(soup_no_year)
        self.assertEqual(len(result_no_year), 1)
        self.assertEqual(result_no_year[0]["year"], "")
        self.assertEqual(result_no_year[0]["link"], "no_year")


class TestParseDateRange(unittest.TestCase):
    """
    Unit tests for parse_date_range function.
    
    Tests parsing of various date formats and ranges.
    """

    def test_parse_date_range_single_date(self):
        """Test parsing a single date without range."""
        start, end = parse_date_range("29 сентября", "2026")
        self.assertEqual(start, "2026-09-29")
        self.assertEqual(end, "2026-09-29")

    def test_parse_date_range_with_dash(self):
        """Test parsing date range with dash separator."""
        start, end = parse_date_range("29 сентября - 02 октября", "2021")
        self.assertEqual(start, "2021-09-29")
        self.assertEqual(end, "2021-10-02")

    def test_parse_date_range_with_different_years(self):
        """Test parsing date range spanning different years."""
        start, end = parse_date_range("31 декабря 2025 - 02 января", "2026")
        self.assertEqual(start, "2025-12-31")
        self.assertEqual(end, "2026-01-02")

    def test_parse_date_range_empty_string(self):
        """Test parsing with empty string."""
        start, end = parse_date_range("", "2026")
        self.assertIsNone(start)
        self.assertIsNone(end)

    def test_parse_date_range_invalid_format(self):
        """Test parsing with invalid date format."""
        start, end = parse_date_range("invalid date", "2026")
        self.assertIsNone(start)
        self.assertIsNone(end)

    def test_parse_date_range_with_different_years_in_range(self):
        """Test parsing date range with years in both parts."""
        start, end = parse_date_range("31 декабря 2025 - 02 января 2026", "2026")
        self.assertEqual(start, "2025-12-31")
        self.assertEqual(end, "2026-01-02")

    def test_parse_date_range_with_em_dash(self):
        """Test parsing date range with em dash (—)."""
        start, end = parse_date_range("29 сентября — 02 октября", "2026")
        self.assertEqual(start, "2026-09-29")
        self.assertEqual(end, "2026-10-02")

    def test_parse_date_range_with_hyphen(self):
        """Test parsing date range with hyphen (-)."""
        start, end = parse_date_range("29 сентября - 02 октября", "2026")
        self.assertEqual(start, "2026-09-29")
        self.assertEqual(end, "2026-10-02")

    def test_parse_date_range_multiple_days(self):
        """Test parsing date range with multiple days."""
        start, end = parse_date_range("01 - 07 марта", "2026")
        self.assertEqual(start, "2026-03-01")
        self.assertEqual(end, "2026-03-07")

    def test_parse_date_range_feb(self):
        """Test parsing February date."""
        start, end = parse_date_range("14 февраля", "2026")
        self.assertEqual(start, "2026-02-14")
        self.assertEqual(end, "2026-02-14")

    def test_parse_date_range_jan(self):
        """Test parsing January date."""
        start, end = parse_date_range("02 января", "2026")
        self.assertEqual(start, "2026-01-02")
        self.assertEqual(end, "2026-01-02")

    if __name__ == "__main__":
        unittest.main()
