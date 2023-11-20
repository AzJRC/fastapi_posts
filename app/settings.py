from pydantic_settings import BaseSettings, SettingsConfigDict

class APISettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    DB_USER: str = "postgres"
    DB_PASSWORD: str 
    DB_HOSTNAME: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str 
    SECRET_KEY: str 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: str = "60"

settings = APISettings()