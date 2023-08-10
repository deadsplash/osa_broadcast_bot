from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    BOT_TOKEN: str = "6674201207:AAFWV4Agjr-Lai4SUYAM3_poPTMPonZefBA"
    POSTGRES_URI: str = "postgresql://bot:osatgbot@94.103.93.61:5432/postgres"
    ENV: str = "DEV"
    ADMIN_CODE: str = "yo2voquqew"


settings = Settings()
