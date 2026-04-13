from pathlib import Path

from agno.agent import Agent
from agno.db.postgres import PostgresDb
from agno.tools.file import FileTools

from wiki_agent.config import get_db_url, get_model
from wiki_agent.prompts.instructions import WIKI_AGENT_INSTRUCTIONS
from wiki_agent.tools.wiki_tools import WikiTools

PROJECT_ROOT = Path(__file__).parent.parent
KB_DIR = PROJECT_ROOT / "knowledge-base"
SOURCES_DIR = KB_DIR / "sources"


def create_wiki_agent() -> Agent:
    db_url = get_db_url()

    return Agent(
        name="Wiki Agent",
        id="wiki-agent",
        model=get_model(),
        description=(
            "A personal knowledge base agent that maintains a structured wiki. "
            "It ingests source documents, builds interlinked wiki pages, answers "
            "queries from the wiki, and performs maintenance."
        ),
        instructions=WIKI_AGENT_INSTRUCTIONS,
        tools=[
            # Read/write access to the wiki (knowledge-base/)
            FileTools(KB_DIR),
            # Wiki-specific operations: read sources, log, lint
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
