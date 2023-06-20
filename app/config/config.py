from pydantic import BaseSettings


class Settings(BaseSettings):
    DB_PASSWORD: str
    DB_USER: str
    DB: str
    DB_HOST: str
    DB_PORT: int
    MONGODB_URL: str
    RABBIT_URL: str

    class Config:
        env_file = './.env'

settings = Settings()
