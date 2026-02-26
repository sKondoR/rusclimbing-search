from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "RusClimbing API"
    VERSION: str = "1.0.0"
    ORIGINS: list = ["https://rusclimbing-search.vercel.app", "http://localhost:3000"]
    BASE_URL: str = "https://rusclimbing.ru/competitions/"
    # API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str | None = os.getenv("DATABASE_URL")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()