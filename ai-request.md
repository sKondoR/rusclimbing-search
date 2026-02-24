/aif-plan I should have a backend on fastapi deployed on vercel with 1 endpoint:
I will send request with parameters: 
 {
    start,
    end,
    ranks: [],
    types: [],
    groups: [],
    disciplines: []
}

ranks = 'Всероссийские' | 'Международные' | Региональные
types = 'competition' | 'festival'
groups = 'adults' | 'younger' | 'teenagers' | 'juniors' | 'v10' | 'v13' | 'v15' | 'v19' | 'v19'
disciplines = 'bouldering' | 'dvoerobye' | 'etalon' | 'skorost' | 'trudnost' | 'sv' | 'mnogobore'

fastapi should send GET request to:
https://rusclimbing.ru/competitions/?year=&start=2000-01-24&end=2026-12-31&ranks%5B%5D=%D0%92%D1%81%D0%B5%D1%80%D0%BE%D1%81%D1%81%D0%B8%D0%B9%D1%81%D0%BA%D0%B8%D0%B5&ranks%5B%5D=%D0%9C%D0%B5%D0%B6%D0%B4%D1%83%D0%BD%D0%B0%D1%80%D0%BE%D0%B4%D0%BD%D1%8B%D0%B5&ranks%5B%5D=%D0%A0%D0%B5%D0%B3%D0%B8%D0%BE%D0%BD%D0%B0%D0%BB%D1%8C%D0%BD%D1%8B%D0%B5&types%5B%5D=book_competition&types%5B%5D=book_festival&types%5B%5D=book_learning&types%5B%5D=book_train&groups%5B%5D=adults&groups%5B%5D=juniors&groups%5B%5D=older&groups%5B%5D=teenagers&groups%5B%5D=younger&groups%5B%5D=v13&groups%5B%5D=v15&groups%5B%5D=v17&groups%5B%5D=v19&groups%5B%5D=v10&disciplines%5B%5D=bouldering&disciplines%5B%5D=dvoerobye&disciplines%5B%5D=etalon&disciplines%5B%5D=skorost&disciplines%5B%5D=trudnost&disciplines%5B%5D=sv&disciplines%5B%5D=mnogobore

and parse html
row will have structure:

<a class="table__content calendar__link" data-accordion="content" href="/competitions/2112eka/">
    <p class="table__text calendar__date"><span>Даты проведения</span>15  - 20 декабря</p>
    <p class="table__text calendar__name"><span>Название мероприятия</span>Всероссийские юношеские соревнования</p>
    <p class="calendar__button calendar__button--up" data-accordion="button">Развернуть</p>
    <p class="table__text calendar__type"><span>Тип</span>С</p>
    <p class="table__text calendar__group">
        <span>Группы</span>
        Ю; С; М; П                            </p>
    <p class="table__text calendar__disciplines">
        <span>Дисциплины</span>s
        Т; Эт                            </p>
    <p class="table__text calendar__location"><span>Локация</span>Екатеринбург</p>
    <p class="calendar__button" data-accordion="button">Свернуть</p>
</a>
where {
    date: 15  - 20 декабря и год '2021' это первые 2 цифры из 2112eka
    link: competitions/2112eka
    name: Всероссийские юношеские соревнования
    location: Екатеринбург
    type: С
    groups: Ю; С; М; П
    disciplines: Т; Эт
}
link is unique and we can use it as id

we should save all data to postgres db also deployed on vercel



