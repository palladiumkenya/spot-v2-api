from pydantic import BaseSettings


class Settings(BaseSettings):
    DB: str
    MONGODB_URL: str
    RABBIT_URL: str
    DB_MSSQL: str
    DB_MSSQL_HOST: str
    DB_MSSQL_USERNAME: str
    DB_MSSQL_PASS: str

    class Config:
        env_file = './.env'

settings = Settings()
