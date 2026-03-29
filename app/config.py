from urllib.parse import quote_plus

from pydantic_settings import BaseSettings
from pydantic import ValidationError, computed_field
from functools import lru_cache


class Settings(BaseSettings):
    MONGO_USER: str
    MONGO_PASSWORD: str
    MONGO_CLUSTER: str
    DATABASE_NAME: str
    APP_ENV: str = "development"

    @computed_field
    @property
    def MONGODB_URI(self) -> str:
        user = quote_plus(self.MONGO_USER)
        password = quote_plus(self.MONGO_PASSWORD)
        return f"mongodb+srv://{user}:{password}@{self.MONGO_CLUSTER}.mongodb.net/"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
