import re
from datetime import datetime, timezone
from pathlib import Path

from agno.tools.toolkit import Toolkit


class WikiTools(Toolkit):
    """Tools for wiki-specific operations: reading sources, managing the index/log, and linting."""

    def __init__(self, sources_dir: Path, kb_dir: Path, **kwargs):
        super().__init__(
            name="wiki_tools",
            tools=[
                self.list_sources,
                self.read_source,
                self.get_wiki_index,
                self.append_to_log,
                self.lint_wiki,
            ],
            instructions=(
                "Use these tools for wiki-specific operations. "
                "Use `list_sources` to see available source documents. "
                "Use `read_source` to read a source file before ingesting it. "
                "Use `get_wiki_index` to see all wiki pages before answering queries. "
                "Use `append_to_log` after every ingest, query-to-page, or lint operation. "
                "Use `lint_wiki` to health-check the wiki."
            ),
            **kwargs,
        )
        self.sources_dir = sources_dir
        self.kb_dir = kb_dir

    def list_sources(self) -> str:
        """List all source documents in the sources directory.

        Returns:
            A formatted list of source filenames, one per line.
        """
        if not self.sources_dir.exists():
            return "Sources directory does not exist."

        files = sorted(
            f.name
            for f in self.sources_dir.iterdir()
            if f.is_file() and f.name != ".gitkeep"
        )
        if not files:
            return "No source documents found."
        return "\n".join(files)

    def read_source(self, filename: str) -> str:
        """Read a source document from the sources directory. Sources are immutable — never modify them.

        Args:
            filename: The name of the source file to read (e.g. 'article-title.md').

        Returns:
            The full text content of the source file.
        """
        path = self.sources_dir / filename
        if not path.exists():
            return f"Source file not found: {filename}"
        if not path.is_file():
            return f"Not a file: {filename}"
        # Prevent path traversal
        try:
            path.resolve().relative_to(self.sources_dir.resolve())
        except ValueError:
            return "Invalid filename: path traversal not allowed."
        return path.read_text(encoding="utf-8")

    def get_wiki_index(self) -> str:
        """Read the wiki index file (index.md) to see all existing wiki pages.

        Returns:
            The full content of index.md, or a message if it doesn't exist.
        """
        index_path = self.kb_dir / "index.md"
        if not index_path.exists():
            return "index.md does not exist yet."
        return index_path.read_text(encoding="utf-8")

    def append_to_log(self, entry: str) -> str:
        """Append a timestamped entry to the operations log (log.md). This is append-only.

        Args:
            entry: A description of the operation performed (e.g. 'Ingested article-title.md — created summary, updated 3 entity pages').

        Returns:
            Confirmation message.
        """
        log_path = self.kb_dir / "log.md"
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        log_entry = f"\n## [{timestamp}] {entry}\n"

        if log_path.exists():
            content = log_path.read_text(encoding="utf-8")
        else:
            content = "# Operations Log\n"

        content += log_entry
        log_path.write_text(content, encoding="utf-8")
        return f"Logged: [{timestamp}] {entry}"

    def lint_wiki(self) -> str:
        """Scan the wiki for health issues: orphan pages, broken links, missing pages, index gaps.

        Returns:
            A report of issues found, or 'No issues found.' if the wiki is healthy.
        """
        if not self.kb_dir.exists():
            return "Knowledge base directory does not exist."

        # Collect all markdown files (excluding .obsidian and sources/)
        md_files: dict[str, str] = {}
        for f in self.kb_dir.rglob("*.md"):
            if ".obsidian" in f.parts or "sources" in f.parts:
                continue
            md_files[f.name] = f.read_text(encoding="utf-8")

        if not md_files:
            return "No markdown files found in knowledge base."

        # Parse links from each file: [text](target.md) pattern
        link_pattern = re.compile(r"\[([^\]]*)\]\(([^)]+\.md)\)")
        outgoing: dict[str, set[str]] = {}
        incoming: dict[str, set[str]] = {name: set() for name in md_files}

        for name, content in md_files.items():
            links = set()
            for match in link_pattern.finditer(content):
                target = match.group(2)
                # Strip relative path prefixes
                target = target.split("/")[-1]
                links.add(target)
                if target in incoming:
                    incoming[target].add(name)
            outgoing[name] = links

        issues = []

        # Orphan pages: no inbound links (except index.md, log.md, overview.md)
        special_pages = {"index.md", "log.md", "overview.md"}
        orphans = [
            name
            for name, sources in incoming.items()
            if not sources and name not in special_pages
        ]
        if orphans:
            issues.append(
                "**Orphan pages** (no inbound links):\n"
                + "\n".join(f"  - {p}" for p in sorted(orphans))
            )

        # Broken links: point to files that don't exist
        broken = []
        for name, links in outgoing.items():
            for target in links:
                if target not in md_files:
                    broken.append(f"  - {name} -> {target}")
        if broken:
            issues.append(
                "**Broken links** (target does not exist):\n"
                + "\n".join(sorted(broken))
            )

        # Pages in wiki but missing from index.md
        index_content = md_files.get("index.md", "")
        missing_from_index = [
            name
            for name in md_files
            if name not in special_pages
            and name != "index.md"
            and name not in index_content
        ]
        if missing_from_index:
            issues.append(
                "**Missing from index.md**:\n"
                + "\n".join(f"  - {p}" for p in sorted(missing_from_index))
            )

        if not issues:
            return "No issues found. Wiki is healthy."

        return "\n\n".join(issues)
