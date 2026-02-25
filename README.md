# RusClimbing Search API

API для поиска соревнований по скалолазанию на основе данных с rusclimbing.ru

## Особенности

- **FastAPI** - современный веб-фреймворк
- **PostgreSQL** - надежная база данных
- **Vercel** - деплой и хостинг
- **BeautifulSoup** - парсер HTML
- **CORS** - кросс-доменные запросы

## Установка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd rusclimbing-search
```

2. Установите зависимости:
```bash
pip install .
```

3. Создайте файл `.env`:
```bash
cp .env.example .env
```

4. Настройте переменные окружения в `.env`:
```env
DATABASE_URL="postgresql://username:password@hostname:5432/database_name"
VERCEL_URL="https://your-app-name.vercel.app"
ALLOWED_ORIGINS=["https://rusclimbing-search.vercel.app", "http://localhost:3000"]
```

## Запуск

### Локальный запуск
```bash
# Разработка
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Продакшн
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Vercel
```bash
# Установка Vercel CLI
npm i -g vercel

# Деплой
vercel --prod
```

## API Эндпоинты

### GET /api/competitions
Получение списка соревнований с фильтрацией

**Параметры запроса:**
- `start` (опционально) - начальная дата (YYYY-MM-DD)
- `end` (опционально) - конечная дата (YYYY-MM-DD)
- `ranks` (опционально) - массив рангов
- `types` (опционально) - массив типов
- `groups` (опционально) - массив групп
- `disciplines` (опционально) - массив дисциплин

**Пример запроса:**
```bash
curl -X GET "http://localhost:8000/api/competitions?start=2024-01-01&end=2024-12-31&types=book_competition&groups=adults"
```

### GET /api/competitions/fetch
Загрузка и сохранение соревнований из источника

**Параметры запроса:**
- `start` (опционально) - начальная дата
- `end` (опционально) - конечная дата
- `ranks` (опционально) - массив рангов
- `types` (опционально) - массив типов
- `groups` (опционально) - массив групп
- `disciplines` (опционально) - массив дисциплин

**Пример запроса:**
```bash
curl -X GET "http://localhost:8000/api/competitions/fetch?start=2024-01-01&end=2024-12-31"
```

## Параметры фильтрации

### Ранги
- `Всероссийские`
- `Международные`
- `Региональные`

### Типы
- `book_competition` - соревнования
- `book_festival` - фестивали
- `book_learning` - обучение
- `book_train` - тренировки

### Группы
- `adults` - взрослые
- `juniors` - юниоры
- `teenagers` - подростки
- `younger` - младшие
- `v10` - ветераны 10
- `v13` - ветераны 13
- `v15` - ветераны 15
- `v19` - ветераны 19

### Дисциплины
- `bouldering` - боулдеринг
- `dvoerobye` - двоеборье
- `etalon` - эталон
- `skorost` - скорость
- `trudnost` - трудность
- `sv` - спортивное восхождение
- `mnogobore` - многоборье

## Структура проекта

```
rusclimbing-search/
├── api/
│   └── main.py          # Основное приложение FastAPI
├── .env                  # Переменные окружения
├── .env.example          # Пример файла окружения
├── requirements.txt       # Зависимости Python
├── package.json          # Зависимости Node.js и конфигурация Vercel
├── README.md             # Документация
└── .gitignore            # Игнорируемые файлы
```

## Деплой на Vercel

1. Создайте аккаунт на [Vercel](https://vercel.com/)
2. Установите Vercel CLI:
   ```bash
   npm i -g vercel
   ```
3. Залогиньтесь:
   ```bash
   vercel login
   ```
4. Деплойте проект:
   ```bash
   vercel --prod
   ```

## База данных

Для работы с PostgreSQL:
1. Создайте базу данных
2. Настройте подключение в `.env`
3. При первом запуске таблицы создадутся автоматически







http://localhost:8000