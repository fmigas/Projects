from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file = '.env',
    )

    MONGODB_USER: str
    MONGODB_PASSWORD: str
    MONGODB_CLUSTER_NAME: str
    MONGODB_DATABASE: str
    MONGODB_COLLECTION_TEXTS: str
    MONGODB_COLLECTION_USERS: str
    MONGODB_COLLECTION_WORDS: str
    MONGODB_COLLECTION_WORDS_RANKING: str

    PONS_SECRET: str

    SQLITE_DATABASE: str

    OPENAI_API_KEY: str
    CHAT_BASIC: str
    CHAT_ADVANCED: str

    VALID_LANGUAGES: list[str]

    example_docs: Path = Path.cwd() / 'files' / 'example_docs'
    logs: Path = Path.cwd() / 'files' / 'logs'


settings = Settings()
