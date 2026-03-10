import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Student AI Assistant"
    DEBUG: bool = False
    SENTRY_DSN: str = ""
    
    # LLM Settings
    OPENAI_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TIMEOUT: int = 30
    LLM_MAX_RETRIES: int = 3
    
    # Caching
    CACHE_TYPE: str = "memory"
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 600
    
    STUDENT_DATA_PATH: str = os.path.join(os.path.dirname(__file__), "../../app/database/students_data.json")

    # Student Identity
    STUDENT_ID_PATTERN: str = r"STU\d{8}"
    STUDENT_ID_EXAMPLE: str = "STU20260001"

    # Chat Input
    MAX_MESSAGE_LENGTH: int = 1000

    # LLM History (token budget for conversation history sent to LLM)
    MAX_HISTORY_TOKENS: int = 1500

    # This tells Pydantic to automatically load from the .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
