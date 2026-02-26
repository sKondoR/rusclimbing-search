import unittest
from bs4 import BeautifulSoup
from parser import parse_events

class TestParseevents(unittest.TestCase):
    
    def test_parse_events(self):
        # Mock HTML content
        html_content = '''
        <li class="table__item" data-accordion="element">
            <a class="table__content calendar__link" data-accordion="content" href="/events/2103voronezh_ch/">
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
            <a class="table__content calendar__link" data-accordion="content" href="/events/2403msk_vs1/">
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
        '''
        
        # Create BeautifulSoup object
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Call the function
        result = parse_events(soup)
        
        # Assert the result
        self.assertEqual(len(result), 2)
        
        event = result[0]
        self.assertEqual(event["date"], "04 - 07 марта 2021")
        self.assertEqual(event["link"], "/events/2103voronezh_ch/")
        self.assertEqual(event["name"], "Чемпионат России")
        self.assertEqual(event["location"], "Воронеж")
        self.assertEqual(event["type"], "С")
        self.assertEqual(event["groups"], ["В"])
        self.assertEqual(event["disciplines"], ["Б"])

        event2 = result[1]
        self.assertEqual(event2["date"], "31 марта - 05 апреля 2024")
        self.assertEqual(event2["link"], "/events/2403msk_vs1/")
        self.assertEqual(event2["name"], "Всероссийские соревнования")
        self.assertEqual(event2["location"], "Москва")
        self.assertEqual(event2["type"], "С")
        self.assertEqual(event2["groups"], ["Ю","С"])
        self.assertEqual(event2["disciplines"], ["Т","Эт"])

if __name__ == '__main__':
    unittest.main()