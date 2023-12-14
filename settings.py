from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GARMIN_USERNAME: SecretStr
    GARMIN_PASSWORD: SecretStr
    FILTER_BEFORE: str = "1970-01-01 00:00:00"

    model_config = SettingsConfigDict(env_file=".env")


conf = Settings()
