from pydantic_settings import BaseSettings , SettingsConfigDict;

class Settings(BaseSettings):
    openai_api_key: str
    openai_model:str ="gpt-5-nano"
    model_config=SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        )
    database_url: str
    langsmith_tracing: bool = False
    langsmith_api_key: str | None = None
    langsmith_project: str = "ai-support-agent"



settings=Settings()