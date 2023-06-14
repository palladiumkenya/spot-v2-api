from pydantic import BaseSettings


class Settings(BaseSettings):
    DB_PASSWORD: str
    DB_USER: str
    DB: str
    DB_HOST: str
    DB_PORT: int
    DHIS2_API_BASE_URL: str
    DHIS2_PASSWORD: str
    DHIS2_USERNAME: str
    

    class Config:
        env_file = './.env'


settings = Settings()

