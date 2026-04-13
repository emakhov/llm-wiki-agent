# LLM Wiki Agent

## Project Overview

Personal knowledge base system where an AI agent (Agno + AgentOS) maintains a structured wiki. The user adds source documents to `sources/`, the agent processes them into interlinked wiki pages in `knowledge-base/`.

## Architecture

The entire `knowledge-base/` directory is an Obsidian vault:
- **`knowledge-base/sources/`** — Immutable source documents. Added by the user (e.g. via Obsidian Web Clipper). The agent reads but NEVER modifies these.
- **`knowledge-base/`** (root) — LLM-generated wiki pages. The agent owns these: creates pages, updates them, maintains cross-references.
- **`wiki_agent/`** — Python agent code using Agno framework + AgentOS runtime.

## Tech Stack

- **Agno** — agent framework (Agent, Toolkit, FileTools)
- **AgentOS** — production runtime with web UI at localhost:7777
- **PostgreSQL + pgvector** — session persistence, vector search
- **uv** — package manager (`uv sync`, `uv run`)

## Key Files

- `wiki_agent/main.py` — AgentOS entry point, initializes Langfuse tracing, creates both agents + knowledge base, serves the app
- `wiki_agent/tracing.py` — Langfuse setup via OpenInference/OpenTelemetry (enabled by `LANGFUSE_ENABLED=true`)
- `wiki_agent/agent.py` — Two agent factories: `create_query_agent()` (read-only wiki access) and `create_maintainer_agent()` (full read/write + ingest/lint)
- `wiki_agent/config.py` — LLM provider selection via `LLM_PROVIDER` env var (claude/openai)
- `wiki_agent/tools/wiki_tools.py` — Custom Toolkit: `list_sources`, `read_source`, `get_wiki_index`, `append_to_log`, `lint_wiki`. Sources dir is `knowledge-base/sources/`.
- `wiki_agent/prompts/instructions.py` — Separate instruction sets: `QUERY_AGENT_INSTRUCTIONS` and `MAINTAINER_AGENT_INSTRUCTIONS`
- `knowledge-base/index.md` — Wiki page catalog (table: Page | Type | Summary | Last Updated)
- `knowledge-base/log.md` — Append-only operations log

## Wiki Conventions

### Page Types
- **summary** — One per source document. Title, summary, key takeaways, source citation.
- **entity** — One per person, organization, or place. Accumulates info across sources.
- **concept** — One per abstract topic. Evolves as sources add depth.
- **comparison** — Side-by-side analysis of entities/concepts.
- **analysis** — Synthesized answers to user questions, filed back into the wiki.
- **overview** — High-level overview of the knowledge base.

### Filenames
- Lowercase kebab-case: `attention-mechanism.md`, `openai-summary.md`
- Summary pages: `<source-name>-summary.md`

### Page Structure
```markdown
# Page Title

Content here. Cross-reference with [Other Page](other-page.md).

## Sources
- [source-filename.md](sources/source-filename.md)
```

### Special Files
- **`index.md`** — Catalog of all pages. Table format: Page | Type | Summary | Last Updated.
- **`log.md`** — Append-only operations log. Timestamped entries.
- **`overview.md`** — High-level description of the knowledge base.

### Cross-References
- Use `[Display Text](filename.md)` format (standard markdown, Obsidian-compatible).
- Every entity/concept page should link to related pages.
- When new information contradicts existing content, note it explicitly and cite both sources.

## Commands

```bash
docker compose up -d              # Start PostgreSQL
uv sync                           # Install dependencies
uv run python -m wiki_agent.main  # Start AgentOS at localhost:7777
```

## Environment Variables
- `LLM_PROVIDER` — `claude`, `openai`, or `openrouter` (default: `claude`)
- `LLM_MODEL` — Model ID override (default depends on provider: `claude-sonnet-4-20250514`, `gpt-4o`, or `anthropic/claude-sonnet-4`)
- `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` / `OPENROUTER_API_KEY` — API keys
- `DATABASE_URL` — PostgreSQL connection (default: `postgresql+psycopg://ai:ai@localhost:5532/ai`)
- `LANGFUSE_ENABLED` — `true` to enable Langfuse tracing (default: `false`)
- `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` — Langfuse API keys
- `LANGFUSE_BASE_URL` — Langfuse endpoint (default: `https://cloud.langfuse.com`)

## Development Notes

- Sources are read-only to the agent — `WikiTools.read_source` provides access but no write tool exists for `knowledge-base/sources/`
- `FileTools` is scoped to `knowledge-base/` for wiki page creation/editing
- `sources/` lives inside `knowledge-base/` so the entire vault is one Obsidian workspace
- `WikiTools` handles structured operations: log is always append-only with timestamps, lint does systematic scanning
- Agent instructions in `prompts/instructions.py` encode the full ingest/query/lint workflows
