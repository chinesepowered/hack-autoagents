from pathlib import Path

from pydantic_settings import BaseSettings

# Find .env in repo root (parent of backend/)
ENV_FILE = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./echomind.db"

    # API Keys
    reka_api_key: str = ""
    modulate_api_key: str = ""
    fastino_api_key: str = ""
    yutori_api_key: str = ""

    # App
    frontend_url: str = "http://localhost:5173"
    environment: str = "development"

    class Config:
        env_file = str(ENV_FILE)


settings = Settings()
