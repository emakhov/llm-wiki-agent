import os

from dotenv import load_dotenv

load_dotenv()


def get_model():
    """Return an Agno model instance based on environment configuration."""
    provider = os.getenv("LLM_PROVIDER", "claude").lower()

    if provider == "claude":
        from agno.models.anthropic import Claude

        model_id = os.getenv("LLM_MODEL", "claude-sonnet-4-20250514")
        return Claude(id=model_id)
    elif provider == "openai":
        from agno.models.openai import OpenAIChat

        model_id = os.getenv("LLM_MODEL", "gpt-4o")
        return OpenAIChat(id=model_id)
    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER: {provider}. Use 'claude' or 'openai'."
        )


def get_db_url() -> str:
    return os.getenv(
        "DATABASE_URL", "postgresql+psycopg://ai:ai@localhost:5532/ai"
    )
