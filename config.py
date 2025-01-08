from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List,Optional
import asyncio
from dotenv import load_dotenv

load_dotenv()
class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    APP_TITLE: str = "API"
    APP_DESCRIPTION: str = "API Documentation"

    ACCESS_TOKEN_EXPIRATION: int = 5 * 60
    REFRESH_TOKEN_EXPIRATION: int = 1 * 24 * 60 * 60

    PRIVATE_KEY: str
    REFRESH_PRIVATE_KEY: str
    PUBLIC_KEY: str
    
    KEY_GENERATE_ENCRYPT: str

    DB: str
    DB_POOL_PRE_PING: bool = True
    DB_POOL_SIZE: int = 20
    DB_POOL_RECYCLE: int = 1800
    DB_ECHO: bool = False

    PORT: int


config = Config()