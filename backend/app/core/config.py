from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent.parent  # теперь это .../backend
ENV_PATH = BASE_DIR / ".env"


class Settings(BaseSettings):
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    SECRET_KEY: str
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    SQLALCHEMY_ECHO: bool = True

    PROJECT_NAME: str
    VERSION: str
    OPENAPI_URL: str = "/api/v1/openapi.json"
    DOCS_URL: str | None = "/docs"
    REDOC_URL: str | None = "/redoc"
    BACKEND_CORS_ORIGINS: list[str] = []
    HOST: str = "localhost"
    PORT: int = 8000
    DEBUG: bool = True

    @property
    def database_url_asyncpg(self):
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

    model_config = SettingsConfigDict(env_file=str(ENV_PATH))


settings = Settings()
