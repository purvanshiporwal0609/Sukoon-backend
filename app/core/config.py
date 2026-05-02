from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    APP_NAME: str = "Sukoon"
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    MONGODB_URL: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
