# CFR-search

Сервис поиска результатов соревнований с сайта Федерации Скалолазанья России.
https://cfr-search.vercel.app/docs

## Описание

Этот проект представляет собой современное REST API для поиска и получения результатов соревнований по скалолазанию, проводимых в России. Данные собираются с официального сайта и структурируются для удобного доступа через REST-интерфейс.

Проект использует современный стек:

- **FastAPI** 0.104.1 - высокопроизводительный веб-фреймворк
- **SQLAlchemy** 2.0.23 - ORM для работы с базой данных
- **Alembic** 1.13.0 - миграции базы данных
- **Pydantic** 2.5.0 - валидация данных
- **asyncpg** 0.29.0 - асинхронный PostgreSQL драйвер

## Структура проекта

```
rusclimbing-search/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/      # API эндпоинты
│   │           ├── events.py   # Эндпоинты для соревнований
│   │           └── teams.py    # Эндпоинты для команд
│   ├── core/
│   │   ├── config.py           # Конфигурация приложения
│   │   ├── exceptions.py       # Пользовательские исключения
│   │   ├── permissions.py      # Проверка прав доступа
│   │   └── db/
│   │       ├── database.py     # Настройка базы данных
│   │       └── session.py      # Сессия базы данных
│   ├── db/
│   │   └── migrations/         # Alembic миграции
│   ├── middleware/
│   │   └── cors.py             # CORS middleware
│   ├── models/
│   │   ├── event.py            # Модель соревнования
│   │   └── team.py             # Модель команды
│   ├── repositories/
│   │   ├── event_repository.py # Репозиторий событий
│   │   └── team_repository.py  # Репозиторий команд
│   ├── schemas/
│   │   ├── event.py            # Схемы событий
│   │   └── team.py             # Схемы команд
│   ├── services/
│   │   ├── event_service.py    # Сервис соревнований
│   │   └── team_service.py     # Сервис команд
│   ├── utils/
│   │   ├── parsers.py          # Парсеры данных
│   │   └── utils.py            # Утилиты
│   ├── tests/
│   │   ├── parser_test.py      # Тесты парсера
│   │   └── run_tests.py        # Запуск тестов
│   └── main.py                 # Точка входа приложения
```

## Зависимости

- **Python** 3.10+
- **FastAPI** 0.104.1 - веб-фреймворк
- **Uvicorn** 0.24.0 - ASGI сервер
- **SQLAlchemy** 2.0.23 - ORM
- **Alembic** 1.13.0 - миграции базы данных
- **Pydantic** 2.5.0 - валидация данных
- **Pydantic-settings** 2.1.0 - настройка конфигурации
- **asyncpg** 0.29.0 - асинхронный PostgreSQL драйвер
- **beautifulsoup4** 4.12.2 - парсинг HTML
- **requests** 2.31.0 - HTTP клиент
- **python-dotenv** 1.0.0 - загрузка .env файлов

## Установка

1. **Клонирование репозитория:**
   ```bash
   git clone <repository-url>
   cd rusclimbing-search
   ```

2. **Установка зависимостей:**
   ```bash
   pip install -e .
   ```

3. **Настройка переменных окружения:**
   ```bash
   cp .env.example .env
   # Отредактируйте .env файл с вашими настройками
   ```

4. **Инициализация базы данных:**
   ```bash
   alembic upgrade head
   ```

## Запуск

### Локальный запуск

```bash
# Режим разработки с автоматической перезагрузкой
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Или через Python
python -m uvicorn app.main:app --reload
```

### Производственный запуск

```bash
# Без автоматической перезагрузки
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Доступ к API

- **API Documentation (Swagger UI)**: http://localhost:8000/docs
- **API Documentation (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Эндпоинты

### Соревнования (Events)

#### GET /api/v1/events

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
curl -X GET "http://localhost:8000/api/v1/events?start=2024-01-01&end=2024-12-31&types=book_competition&groups=adults"
```

#### GET /api/v1/events/{event_id}

Получение информации о конкретном соревновании

**Пример запроса:**

```bash
curl -X GET "http://localhost:8000/api/v1/events/1"
```

#### GET /api/v1/events/fetch

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
curl -X GET "http://localhost:8000/api/v1/events/fetch?start=2024-01-01&end=2024-12-31"
```

### Команды (Teams)

#### GET /api/v1/teams

Получение списка команд

**Пример запроса:**

```bash
curl -X GET "http://localhost:8000/api/v1/teams"
```

#### GET /api/v1/teams/{team_id}

Получение информации о конкретной команде

**Пример запроса:**

```bash
curl -X GET "http://localhost:8000/api/v1/teams/1"
```

## Параметры фильтрации на сайте Федерации Скалолазанья России

### Ранги (Ranks)

- `Всероссийские` (national)
- `Международные` (international)
- `Региональные` (regional)

### Типы (Types)

- `book_competition` - соревнования
- `book_festival` - фестивали
- `book_learning` - обучение
- `book_train` - тренировки

### Группы (Groups)

- `adults` - взрослые до 2026 г.
  до 2026 г.
- `juniors` - юниоры 18-19 лет
- `older` - юноши, девушки 16-17 лет
- `younger` - юноши, девушки 14-15 лет
- `teenagers` - юноши, девушки 10-13 лет
  с 2026 г.
- `v10` - юноши, девушки 10-12 лет
- `v13` - юноши, девушки 13-14 лет
- `v15` - юноши, девушки 15-16 лет
- `v17` - юноши, девушки 17-18 лет
- `v19` - юниоры 19-20 лет

### Дисциплины (Disciplines)

- `bouldering` - боулдеринг
- `dvoerobye` - двоеборье
- `etalon` - эталон
- `skorost` - скорость
- `trudnost` - трудность
- `sv` - спортивное восхождение
- `mnogobore` - многоборье

## Тестирование

pytest

### Линтинг

pylint, ruff

## Разработка

### Архитектура

Проект использует архитектуру на основе слоёв (Layered Architecture):

1. **API Layer** ([`app/api/v1/endpoints/`](app/api/v1/endpoints/)) - обработка HTTP запросов
2. **Service Layer** ([`app/services/`](app/services/)) - бизнес-логика
3. **Repository Layer** ([`app/repositories/`](app/repositories/)) - работа с данными
4. **Model Layer** ([`app/models/`](app/models/)) - ORM модели
5. **Schema Layer** ([`app/schemas/`](app/schemas/)) - Pydantic схемы

## Дополнительные ресурсы

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Vercel Documentation](https://vercel.com/docs)
