import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)
    # Service Configuration
    SERVICE_NAME: str = "auth-service"
    SERVICE_PORT: int = 3002
    ENVIRONMENT: str = "development"
    
    # JWT Configuration
    JWT_SECRET_KEY: Optional[str] = None  # Required: set via environment variable
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    REFRESH_TOKEN_EXPIRATION_DAYS: int = 30
    
    # Salesforce OAuth
    SF_CLIENT_ID: Optional[str] = None
    SF_CLIENT_SECRET: Optional[str] = None
    
    # Database
    DATABASE_URL: str = "postgresql://reports_user:secure_password@localhost:5432/reports_db"
    
    # Cache
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Security
    BCRYPT_ROUNDS: int = 12
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15
    
    # RBAC
    ENABLE_RBAC: bool = True

settings = Settings()
