from pydantic import BaseSettings


class Settings(BaseSettings):
    DB: str
    MONGODB_URL: str
    RABBIT_URL: str

    class Config:
        env_file = './.env'

settings = Settings()
