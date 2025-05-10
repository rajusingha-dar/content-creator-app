import os
import logging
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Database settings
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "password")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "3306")
    DB_NAME: str = os.getenv("DB_NAME", "content_creator_db")
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default-secret-key-change-this")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Application settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Logging settings
    LOG_LEVEL: int = getattr(logging, os.getenv("LOG_LEVEL", "INFO"))
    LOG_FILE: str = os.getenv("LOG_FILE", "app.log")

settings = Settings()