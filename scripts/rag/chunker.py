#!/usr/bin/env python3
"""
---
id: SCRIPT-0071
type: script
owner: platform-team
status: active
maturity: 1
last_validated: 2026-01-28
test:
  runner: pytest
  command: "pytest -q tests/unit/test_chunker.py"
  evidence: declared
dry_run:
  supported: false
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
relates_to:
  - GOV-0017-tdd-and-determinism
  - ADR-0184-rag-markdown-header-chunking
  - PRD-0008-governance-rag-pipeline
---
Purpose: RAG Markdown Chunker for GoldenPath governance documents.

Splits markdown documents on H2 (##) header boundaries per ADR-0184.
Each section becomes a chunk with preserved document metadata.

Chunking Parameters (from ADR-0184):
- Split boundary: ## (H2 headers)
- Include header: Yes
- Max chunk size: 1024 tokens (not enforced in Phase 0)
- Min chunk size: 50 tokens (not enforced in Phase 0)
- Overlap: 0 tokens (sections are self-contained)

Example:
    >>> from scripts.rag.chunker import chunk_markdown
    >>> content = "## Section A\\nContent A\\n\\n## Section B\\nContent B"
    >>> chunks = chunk_markdown(content, {"doc_id": "DOC-001"})
    >>> len(chunks)
    2
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import re

from scripts.rag.loader import GovernanceDocument


@dataclass
class Chunk:
    """
    Represents a chunk of document content with metadata.

    Attributes:
        text: The chunk content including section header.
        metadata: Dictionary of metadata (inherited from doc + section-specific).
    """

    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)


# Regex pattern for H2 headers (## Header Text)
H2_PATTERN = re.compile(r"^(##\s+.+)$")
# Regex pattern for fenced code blocks (``` or ~~~)
FENCE_PATTERN = re.compile(r"^\s*(```|~~~)")


def extract_section_name(header_line: str) -> str:
    """
    Extract the section name from an H2 header line.

    Args:
        header_line: Line starting with "## " (e.g., "## Purpose").

    Returns:
        The section name without the ## prefix.

    Example:
        >>> extract_section_name("## Core Principle")
        'Core Principle'
    """
    # Remove ## prefix and strip whitespace
    return header_line.lstrip("#").strip()


def split_on_h2(content: str) -> List[tuple[Optional[str], str]]:
    """
    Split content on H2 (##) headers.

    Args:
        content: Markdown content to split.

    Returns:
        List of (header, content) tuples. First item may have header=None
        if content starts before any H2 header.

    Example:
        >>> parts = split_on_h2("Intro\\n\\n## A\\nContent A\\n\\n## B\\nContent B")
        >>> len(parts)
        3
    """
    if not content or not content.strip():
        return []

    # Find all H2 header positions, ignoring fenced code blocks
    matches = []
    in_fence = False
    cursor = 0

    for line in content.splitlines(keepends=True):
        if FENCE_PATTERN.match(line):
            in_fence = not in_fence
        if not in_fence:
            header_match = H2_PATTERN.match(line)
            if header_match:
                header_line = header_match.group(1).rstrip("\n")
                matches.append((cursor, header_line))
        cursor += len(line)

    if not matches:
        # No H2 headers - return entire content as single section
        return [(None, content)]

    sections = []

    # Handle content before first H2 (if any)
    first_match_pos, _ = matches[0]
    if first_match_pos > 0:
        intro_content = content[:first_match_pos].strip()
        if intro_content:
            sections.append((None, intro_content))

    # Process each H2 section
    for i, (start_pos, header) in enumerate(matches):

        # Determine end of this section
        if i + 1 < len(matches):
            end_pos = matches[i + 1][0]
        else:
            end_pos = len(content)

        # Extract section content (including header)
        section_content = content[start_pos:end_pos].strip()
        sections.append((header, section_content))

    return sections


def chunk_markdown(content: str, base_metadata: Dict[str, Any]) -> List[Chunk]:
    """
    Split markdown content into chunks on H2 header boundaries.

    Per ADR-0184, each H2 section becomes a separate chunk with:
    - Section content (including the header)
    - Document metadata (inherited)
    - Section-specific metadata (section name, header level, chunk index)

    Args:
        content: Markdown content to chunk.
        base_metadata: Metadata to inherit for all chunks (from document).

    Returns:
        List of Chunk objects.

    Example:
        >>> chunks = chunk_markdown("## A\\nContent A\\n\\n## B\\nContent B", {})
        >>> len(chunks)
        2
    """
    if not content or not content.strip():
        return []

    sections = split_on_h2(content)
    chunks = []

    for idx, (header, section_content) in enumerate(sections):
        # Build chunk metadata
        chunk_metadata = dict(base_metadata)  # Copy base metadata
        chunk_metadata["chunk_index"] = idx
        chunk_metadata["header_level"] = 2 if header else 1

        if header:
            chunk_metadata["section"] = extract_section_name(header)
        else:
            chunk_metadata["section"] = "Introduction"

        chunks.append(
            Chunk(
                text=section_content,
                metadata=chunk_metadata,
            )
        )

    return chunks


def chunk_document(doc: GovernanceDocument) -> List[Chunk]:
    """
    Chunk a GovernanceDocument into sections.

    Convenience function that extracts metadata from the document
    and passes it to chunk_markdown.

    Args:
        doc: GovernanceDocument to chunk.

    Returns:
        List of Chunk objects with inherited document metadata.

    Example:
        >>> from scripts.rag.loader import load_governance_document
        >>> doc = load_governance_document("docs/GOV-0017.md")
        >>> chunks = chunk_document(doc)
        >>> chunks[0].metadata["doc_id"]
        'GOV-0017-tdd-and-determinism'
    """
    # Build base metadata for chunks
    base_metadata = {
        "doc_id": doc.metadata.get("id"),
        "doc_title": doc.metadata.get("title"),
        "doc_type": doc.metadata.get("type"),
        "file_path": doc.metadata.get("file_path") or str(doc.source_path),
    }

    # Add relates_to if present
    if "relates_to" in doc.metadata:
        base_metadata["relates_to"] = doc.metadata["relates_to"]

    return chunk_markdown(doc.content, base_metadata)
