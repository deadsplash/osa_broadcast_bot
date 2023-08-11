from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    BOT_TOKEN: str = ""
    POSTGRES_URI: str = ""
    ENV: str = "DEV"


settings = Settings()
