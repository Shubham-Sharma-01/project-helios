"""Application configuration management."""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # App Settings
    app_name: str = Field(default="DevOps Command Center", env="APP_NAME")
    flask_env: str = Field(default="development", env="FLASK_ENV")
    flask_debug: bool = Field(default=True, env="FLASK_DEBUG")
    secret_key: str = Field(default="dev-secret-key", env="SECRET_KEY")
    port: int = Field(default=5000, env="PORT")
    
    # Database
    database_url: str = Field(
        default="sqlite:///devops_command_center.db", 
        env="DATABASE_URL"
    )
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # Slack
    slack_bot_token: Optional[str] = Field(default=None, env="SLACK_BOT_TOKEN")
    slack_app_token: Optional[str] = Field(default=None, env="SLACK_APP_TOKEN")
    slack_signing_secret: Optional[str] = Field(default=None, env="SLACK_SIGNING_SECRET")
    slack_workspace_id: Optional[str] = Field(default=None, env="SLACK_WORKSPACE_ID")
    
    # Anthropic
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(
        default="claude-sonnet-4-20250514", 
        env="ANTHROPIC_MODEL"
    )
    
    # MCP Configuration
    mcp_argocd_enabled: bool = Field(default=False, env="MCP_ARGOCD_ENABLED")
    mcp_argocd_server_url: Optional[str] = Field(default=None, env="MCP_ARGOCD_SERVER_URL")
    mcp_argocd_auth_token: Optional[str] = Field(default=None, env="MCP_ARGOCD_AUTH_TOKEN")
    
    mcp_github_enabled: bool = Field(default=False, env="MCP_GITHUB_ENABLED")
    mcp_github_token: Optional[str] = Field(default=None, env="MCP_GITHUB_TOKEN")
    
    mcp_jira_enabled: bool = Field(default=False, env="MCP_JIRA_ENABLED")
    mcp_jira_url: Optional[str] = Field(default=None, env="MCP_JIRA_URL")
    mcp_jira_email: Optional[str] = Field(default=None, env="MCP_JIRA_EMAIL")
    mcp_jira_api_token: Optional[str] = Field(default=None, env="MCP_JIRA_API_TOKEN")
    
    # Notifications
    notification_check_interval: int = Field(default=300, env="NOTIFICATION_CHECK_INTERVAL")
    enable_email_notifications: bool = Field(default=False, env="ENABLE_EMAIL_NOTIFICATIONS")
    smtp_server: Optional[str] = Field(default=None, env="SMTP_SERVER")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    
    # AI Settings
    ai_task_priority_threshold: int = Field(default=7, env="AI_TASK_PRIORITY_THRESHOLD")
    ai_auto_categorize: bool = Field(default=True, env="AI_AUTO_CATEGORIZE")
    ai_summary_enabled: bool = Field(default=True, env="AI_SUMMARY_ENABLED")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

