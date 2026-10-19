"""Shared configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central config — reads from .env automatically."""

    # AI
    anthropic_api_key: str = ""

    # Task 1
    knowledge_brain_port: int = 8001
    help_center_url: str = "https://help.brilliantdirectories.com"
    crawl_schedule_hours: int = 24
    expert_email: str = "expert@example.com"

    # Task 2
    inbox_agent_port: int = 8002
    knowledge_brain_api: str = "http://localhost:8001"

    # Task 3
    meeting_scope_port: int = 8003

    # Models
    primary_model: str = "claude-sonnet-4-20250514"
    comparison_model: str = "claude-haiku-4-20250514"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
