from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Malawi Verified Services Hub"

    DATABASE_URL: str = "sqlite:///./verified_services.db"

    SECRET_KEY: str = "CHANGE_ME"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )


settings = Settings()