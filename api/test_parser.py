import unittest
from bs4 import BeautifulSoup
from parser import parse_competitions

class TestParseCompetitions(unittest.TestCase):
    
    def test_parse_competitions(self):
        # Mock HTML content
        html_content = '''
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
        '''
        
        # Create BeautifulSoup object
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Call the function
        result = parse_competitions(soup)
        
        # Assert the result
        self.assertEqual(len(result), 2)
        
        competition = result[0]
        self.assertEqual(competition["date"], "04 - 07 марта 2021")
        self.assertEqual(competition["link"], "/competitions/2103voronezh_ch/")
        self.assertEqual(competition["name"], "Чемпионат России")
        self.assertEqual(competition["location"], "Воронеж")
        self.assertEqual(competition["type"], "С")
        self.assertEqual(competition["groups"], ["В"])
        self.assertEqual(competition["disciplines"], ["Б"])

        competition2 = result[1]
        self.assertEqual(competition2["date"], "31 марта - 05 апреля 2024")
        self.assertEqual(competition2["link"], "/competitions/2403msk_vs1/")
        self.assertEqual(competition2["name"], "Всероссийские соревнования")
        self.assertEqual(competition2["location"], "Москва")
        self.assertEqual(competition2["type"], "С")
        self.assertEqual(competition2["groups"], ["Ю","С"])
        self.assertEqual(competition2["disciplines"], ["Т","Эт"])

if __name__ == '__main__':
    unittest.main()