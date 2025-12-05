import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "LangGraph Agent API"
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = ["http://localhost:8080", "http://localhost:5173"]
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///agents.db")
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default_secret_key_for_development_only")
    
    # LLM API Keys (should be set in environment variables)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # Mem0 API Key (for memory functionality)
    MEM0_API_KEY: str = os.getenv("MEM0_API_KEY", "")
    
    # Redis settings (for caching and message queue)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Observability settings
    ENABLE_TRACING: bool = os.getenv("ENABLE_TRACING", "false").lower() in ("1", "true", "yes", "on")
    
    # MCP Tools settings
    # Maximum number of MCP tools to load per agent to prevent token overflow
    # Set MAX_MCP_TOOLS_PER_AGENT in the environment if you want to enforce a limit.
    # Default of 0 means "no limit" so all MCP tools remain available.
    MAX_MCP_TOOLS_PER_AGENT: int = int(os.getenv("MAX_MCP_TOOLS_PER_AGENT", "0"))

    # OpenTelemetry / Traceloop
    TRACELOOP_BASE_URL: Optional[str] = None
    OTEL_EXPORTER_OTLP_ENDPOINT: Optional[str] = None
    JAEGER_QUERY_URL: Optional[str] = os.getenv("JAEGER_QUERY_URL", "http://jaeger:16686")
    
    class Config:
        case_sensitive = True

settings = Settings()