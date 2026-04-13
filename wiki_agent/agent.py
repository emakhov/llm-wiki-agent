from pathlib import Path

from agno.agent import Agent
from agno.db.postgres import PostgresDb
from agno.tools.file import FileTools

from wiki_agent.config import get_db_url, get_model
from wiki_agent.prompts.instructions import (
    MAINTAINER_AGENT_INSTRUCTIONS,
    QUERY_AGENT_INSTRUCTIONS,
)
from wiki_agent.tools.wiki_tools import WikiTools

PROJECT_ROOT = Path(__file__).parent.parent
KB_DIR = PROJECT_ROOT / "knowledge-base"
SOURCES_DIR = KB_DIR / "sources"


def create_query_agent() -> Agent:
    db_url = get_db_url()

    return Agent(
        name="Query Agent",
        id="query-agent",
        model=get_model(),
        description=(
            "Answers questions by searching and reading the wiki. "
            "Read-only access — does not create or modify pages."
        ),
        instructions=QUERY_AGENT_INSTRUCTIONS,
        tools=[
            # Read-only access to wiki pages
            FileTools(
                KB_DIR,
                enable_save_file=False,
                enable_read_file=True,
                enable_search_files=True,
                enable_list_files=True,
            ),
            # Only the index tool — no source reading, logging, or linting
            WikiTools(
                sources_dir=SOURCES_DIR,
                kb_dir=KB_DIR,
                include_tools=["get_wiki_index"],
            ),
        ],
        db=PostgresDb(db_url=db_url),
        enable_session_summaries=True,
        enable_user_memories=True,
        add_history_to_context=True,
        num_history_runs=5,
        add_datetime_to_context=True,
        markdown=True,
    )


def create_maintainer_agent() -> Agent:
    db_url = get_db_url()

    return Agent(
        name="Maintainer Agent",
        id="maintainer-agent",
        model=get_model(),
        description=(
            "Maintains the wiki: ingests source documents, creates and updates pages, "
            "manages cross-references, and performs health checks."
        ),
        instructions=MAINTAINER_AGENT_INSTRUCTIONS,
        tools=[
            # Full read/write access to wiki pages
            FileTools(KB_DIR),
            # All wiki operations: sources, index, log, lint
            WikiTools(sources_dir=SOURCES_DIR, kb_dir=KB_DIR),
        ],
        db=PostgresDb(db_url=db_url),
        enable_session_summaries=True,
        enable_user_memories=True,
        add_history_to_context=True,
        num_history_runs=5,
        add_datetime_to_context=True,
        markdown=True,
    )
