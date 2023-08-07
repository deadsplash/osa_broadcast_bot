from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    BOT_TOKEN: str = "6674201207:AAFWV4Agjr-Lai4SUYAM3_poPTMPonZefBA"
    POSTGRES_URI: str = ""


settings = Settings()
