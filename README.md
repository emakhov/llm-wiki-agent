# LLM Wiki Agent

A personal knowledge base maintained by an AI agent. You add source documents, the agent builds and maintains a structured, interlinked wiki of markdown files.

Built with [Agno](https://github.com/agno-agi/agno) and [AgentOS](https://docs.agno.com/agent-os/overview).

## How it works

1. **Add sources** — drop articles, papers, or notes into `knowledge-base/sources/` (e.g. via [Obsidian Web Clipper](https://obsidian.md/clipper))
2. **Ingest** — tell the agent to process a source. It reads the document, creates summary and entity pages, updates cross-references, and logs the operation
3. **Query** — ask questions. The agent searches the wiki, reads relevant pages, and synthesizes answers with citations. Good answers get filed back as wiki pages
4. **Lint** — ask the agent to health-check the wiki. It finds orphan pages, broken links, and missing cross-references

The wiki lives in `knowledge-base/` and is fully compatible with [Obsidian](https://obsidian.md) — open it as a vault to browse pages and view the graph.

## Architecture

```
knowledge-base/     # Obsidian vault (open this as your vault)
  sources/          # Immutable source documents (you manage these)
  index.md          # Catalog of all pages
  log.md            # Chronological operations log
  overview.md       # KB overview
  .obsidian/        # Obsidian config
wiki_agent/         # Agent code
  main.py           # AgentOS entry point (serves at localhost:7777)
  agent.py          # Agent definition with tools
  config.py         # LLM model selection
  tools/            # Custom WikiTools toolkit
  prompts/          # Agent instructions
```

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [Docker](https://www.docker.com/) (for PostgreSQL)
- An API key for [Anthropic](https://console.anthropic.com/) or [OpenAI](https://platform.openai.com/)

## Setup

```bash
# 1. Start PostgreSQL + pgvector
docker compose up -d

# 2. Install dependencies
uv sync

# 3. Configure environment
cp .env .env.local  # optional — edit .env directly
# Set your API key:
#   ANTHROPIC_API_KEY=sk-ant-...
# Or for OpenAI:
#   LLM_PROVIDER=openai
#   OPENAI_API_KEY=sk-...

# 4. Start the agent
uv run python -m wiki_agent.main
```

Open [http://localhost:7777](http://localhost:7777) to interact with the Wiki Agent.

## Usage

### Ingest a source

Drop a markdown file into `knowledge-base/sources/`, then tell the agent:

> Ingest article-title.md

The agent will:
- Read the source document
- Create a summary page in the wiki
- Create or update entity/concept pages
- Add cross-references between pages
- Update `index.md` and `log.md`

### Query the wiki

Ask any question:

> What are the key differences between X and Y?

The agent searches the wiki index, reads relevant pages, and synthesizes an answer. If the answer is substantial, it offers to save it as a new wiki page.

### Lint the wiki

> Lint the wiki

The agent scans for orphan pages, broken links, pages missing from the index, and other issues.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `claude` | `claude` or `openai` |
| `LLM_MODEL` | `claude-sonnet-4-20250514` | Model ID override |
| `ANTHROPIC_API_KEY` | — | Required if using Claude |
| `OPENAI_API_KEY` | — | Required if using OpenAI |
| `DATABASE_URL` | `postgresql+psycopg://ai:ai@localhost:5532/ai` | PostgreSQL connection |

## Tips

- Open `knowledge-base/` as an Obsidian vault — sources and wiki pages live together
- **Obsidian Web Clipper** converts web articles to markdown — clip directly into `knowledge-base/sources/`
- **Obsidian graph view** shows the shape of your wiki: hubs, orphans, connections
- The wiki is just a git repo of markdown files — you get version history for free
- Ingest sources one at a time and stay involved for best results
