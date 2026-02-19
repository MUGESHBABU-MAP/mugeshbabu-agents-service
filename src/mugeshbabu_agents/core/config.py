import os
from typing import Optional, Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppConfig(BaseSettings):
    """General application settings."""
    env: Literal["development", "production", "testing"] = Field("development", alias="APP_ENV")
    log_level: str = "INFO"
    project_name: str = "BabuAI Agents Service"
    debug: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

class MongoConfig(BaseSettings):
    """MongoDB configuration."""
    uri: str = Field("mongodb://localhost:27017", alias="MONGO_URI")
    db_name: str = Field("babuai-masterdb", alias="MONGO_DB_NAME")
    min_pool_size: int = 10
    max_pool_size: int = 100

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

class RedisConfig(BaseSettings):
    """Redis configuration."""
    url: str = Field("redis://localhost:6379/0", alias="REDIS_URL")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

class AWSConfig(BaseSettings):
    """AWS configuration."""
    region: str = Field("us-east-1", alias="AWS_REGION")
    access_key_id: Optional[str] = Field(None, alias="AWS_ACCESS_KEY_ID")
    secret_access_key: Optional[str] = Field(None, alias="AWS_SECRET_ACCESS_KEY")
    sqs_queue_url: Optional[str] = Field(None, alias="AWS_SQS_QUEUE_URL")
    
    # Bedrock specific
    bedrock_model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

class AuthConfig(BaseSettings):
    """Authentication configuration."""
    jwt_secret: str = Field("change_me_in_production", alias="SECRET_KEY")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

class Settings(BaseSettings):
    """Global settings container."""
    app: AppConfig = Field(default_factory=AppConfig)
    mongo: MongoConfig = Field(default_factory=MongoConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    aws: AWSConfig = Field(default_factory=AWSConfig)
    auth: AuthConfig = Field(default_factory=AuthConfig)

    def load_secrets(self):
        """
        Placeholder for loading secrets from a Secret Manager (e.g., AWS Secrets Manager, Vault).
        In a real production environment, this would fetch secrets at runtime.
        """
        if self.app.env == "production":
            # Logic to fetch secrets and update config values
            # e.g., self.mongo.uri = fetch_secret("mongo_uri")
            pass

settings = Settings()
