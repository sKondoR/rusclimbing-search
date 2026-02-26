from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "RusClimbing API"
    VERSION: str = "1.0.0"
    ORIGINS: list = ["https://rusclimbing-search.vercel.app", "http://localhost:3000"]
    BASE_URL: str = "https://rusclimbing.ru/competitions/"
    # API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str | None = None

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    def get_db_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL

settings = Settings()