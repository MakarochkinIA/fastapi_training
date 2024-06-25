from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MAIN_HOST: str = 'http://localhost:8000'
    REDIS_HOST: str = 'localhost'
    REDIS_PORT: str = '6379'
    PUSH_NOTIFICATIONS_CHANNEL: str = 'follow'


settings = Settings()  # type: ignore
