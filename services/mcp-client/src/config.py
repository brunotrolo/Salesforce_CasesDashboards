import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)
    # Salesforce OAuth
    SF_CLIENT_ID: str
    SF_CLIENT_SECRET: str
    SF_REFRESH_TOKEN: Optional[str] = None
    SF_INSTANCE_URL: str = "https://login.salesforce.com"
    SF_REDIRECT_URI: Optional[str] = None
    
    # Service Configuration
    SERVICE_NAME: str = "mcp-client"
    SERVICE_PORT: int = 3005
    API_VERSION: str = "v1"
    ENVIRONMENT: str = "development"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Database
    DATABASE_URL: str = "postgresql://reports_user:secure_password@localhost:5432/reports_db"
    
    # Cache
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 3600
    
    # Elasticsearch
    ELASTICSEARCH_HOST: str = "localhost:9200"
    ELASTICSEARCH_INDEX_PREFIX: str = "reports"
    
    # Tracing
    TRACE_SAMPLE_RATE: float = 0.1
    JAEGER_ENABLED: bool = False
    JAEGER_HOST: str = "localhost"
    JAEGER_PORT: int = 6831
    
    # OAuth Configuration
    OAUTH_TIMEOUT: int = 30
    OAUTH_RETRY_ATTEMPTS: int = 3
    OAUTH_RETRY_DELAY: int = 2

settings = Settings()
