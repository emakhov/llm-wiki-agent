import logging
import os

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def get_model():
    """Return an Agno model instance based on environment configuration."""
    provider = os.getenv("LLM_PROVIDER", "claude").lower()

    if provider == "claude":
        from agno.models.anthropic import Claude

        model_id = os.getenv("LLM_MODEL", "claude-sonnet-4-20250514")
        model = Claude(id=model_id)
    elif provider == "openai":
        from agno.models.openai import OpenAIChat

        model_id = os.getenv("LLM_MODEL", "gpt-4o")
        model = OpenAIChat(id=model_id)
    elif provider == "openrouter":
        from agno.models.openrouter import OpenRouter

        model_id = os.getenv("LLM_MODEL", "anthropic/claude-sonnet-4")
        model = OpenRouter(id=model_id)
    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER: {provider}. Use 'claude', 'openai', or 'openrouter'."
        )

    logger.info("Using LLM provider=%s model=%s", provider, model_id)
    return model


def get_db_url() -> str:
    return os.getenv(
        "DATABASE_URL", "postgresql+psycopg://ai:ai@localhost:5532/ai"
    )
