from urllib.parse import quote_plus
from pydantic_settings import BaseSettings, SettingsConfigDict # Added SettingsConfigDict
from pydantic import computed_field
from functools import lru_cache

class Settings(BaseSettings):
    MONGO_USER: str
    MONGO_PASSWORD: str
    MONGO_CLUSTER: str
    DATABASE_NAME: str
    APP_ENV: str = "development"

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1430

    @computed_field
    @property
    def MONGODB_URI(self) -> str:
        user = quote_plus(self.MONGO_USER)
        password = quote_plus(self.MONGO_PASSWORD)
        return f"mongodb+srv://{user}:{password}@{self.MONGO_CLUSTER}.mongodb.net/"

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"  
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()