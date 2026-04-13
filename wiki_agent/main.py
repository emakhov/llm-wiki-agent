import logging

logging.basicConfig(level=logging.INFO)

from agno.db.postgres import PostgresDb
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.os import AgentOS
from agno.vectordb.pgvector import PgVector, SearchType

from wiki_agent.agent import create_maintainer_agent, create_query_agent
from wiki_agent.config import get_db_url
from wiki_agent.tracing import setup_langfuse

setup_langfuse()

db_url = get_db_url()

query_agent = create_query_agent()
maintainer_agent = create_maintainer_agent()

# Vector knowledge base for semantic search over wiki content
wiki_knowledge = Knowledge(
    name="Wiki Knowledge",
    description="Semantic search over wiki pages and source documents",
    contents_db=PostgresDb(
        db_url=db_url,
        id="wiki_knowledge_db",
        knowledge_table="wiki_knowledge_contents",
    ),
    vector_db=PgVector(
        db_url=db_url,
        table_name="wiki_knowledge_vectors",
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    ),
)

agent_os = AgentOS(
    description="LLM Wiki — Personal Knowledge Base",
    agents=[query_agent, maintainer_agent],
    knowledge=[wiki_knowledge],
)

app = agent_os.get_app()


def main():
    agent_os.serve(app="wiki_agent.main:app", reload=True)


if __name__ == "__main__":
    main()
