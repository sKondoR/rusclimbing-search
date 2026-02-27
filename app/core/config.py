
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
    DATABASE_URL: str = None
    BASE_URL: str = "https://www.rusclimbing.ru/competitions/"
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
