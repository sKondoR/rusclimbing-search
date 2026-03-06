from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        PROJECT_NAME: Name of the application
        VERSION: Application version
        DATABASE_URL: Database connection URL
        BASE_URL: Base URL for fetching climbing competition data
        ORIGINS: List of allowed CORS origins
    """

    PROJECT_NAME: str = "rusclimbing-search"
    VERSION: str = "1.0.0"
    DATABASE_URL: str
    BASE_URL: str = "https://www.rusclimbing.ru/competitions/"
    # Live results URL template for teams searching
    LIVE_RESULTS_BASE_URL: str = "https://c-f-r.ru/live/"
    LIVE_RESULTS_PATH: str = "l_q_f13.html"
    # Event filter constants
    EVENT_NAME: str = "Всероссийские соревнования"
    EVENT_YEAR: str = "2026"
    EVENT_GROUP: str = "13-14"
    # Words that should filter out events
    REJECTED_WORDS: list = ["ОТМЕНЕНО", "ОТМЕНЕНЫ"]
    ORIGINS: list = ["*"]


class Config:
    """
    Pydantic configuration settings.

    Attributes:
        env_file: Path to environment variables file
        case_sensitive: Whether environment variable names are case-sensitive
    """

    env_file = ".env"
    case_sensitive = True


settings = Settings()
