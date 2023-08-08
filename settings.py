from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    BOT_TOKEN: str = ""
    POSTGRES_URI: str = "postgresql://bot:osatgbot@0.0.0.0:5432/postgres"
    ENV: str = ""
    ADMIN_CODE: str = ""


settings = Settings()
