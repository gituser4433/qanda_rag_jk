from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()  # Loads .env file from root

class Settings(BaseSettings):
    DATABASE_URL: str
    OPENAI_API_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env",               # Points to your environment file
        env_file_encoding="utf-8"
    )

Config = Settings()

print("✅ DATABASE_URL Loaded from env:", Config.DATABASE_URL)
