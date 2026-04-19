from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Supabase
    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: str
    storage_bucket: str = "pdf-files"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Groq LLM
    groq_api_key: str

    # App Config
    port: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
