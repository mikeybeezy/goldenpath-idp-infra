---
id: ADR-0184-rag-markdown-header-chunking
title: RAG Markdown Header Chunking Strategy
type: adr
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
schema_version: 1
relates_to:
  - GOV-0020-rag-maturity-model
  - PRD-0008-governance-rag-pipeline
  - EC-0017-platform-distribution-framework
supersedes: []
superseded_by: []
tags:
  - rag
  - chunking
  - llm
  - embeddings
inheritance: {}
supported_until: '2028-01-01'
effective_date: 2026-01-28
review_date: 2026-07-28
---

# ADR-0184: RAG Markdown Header Chunking Strategy

## Status

**Accepted**

## Context

The Agentic Graph RAG pipeline (PRD-0008) requires a chunking strategy to split governance documents into embeddable units. The choice of chunking strategy significantly impacts:

1. **Retrieval quality** - Chunks must be semantically coherent
2. **Context preservation** - Related information should stay together
3. **Embedding efficiency** - Chunks must fit within model token limits
4. **Metadata extraction** - Chunk boundaries should align with document structure

### Chunking Strategy Options

| Strategy | Description | Pros | Cons |
|----------|-------------|------|------|
| **Fixed-size** | Split every N tokens | Simple, predictable | Breaks mid-sentence, loses context |
| **Recursive** | Split by separators (paragraphs → sentences) | Flexible | May still break semantic units |
| **Semantic** | ML-based topic boundary detection | Intelligent splits | Slow, complex, requires model |
| **Markdown Headers** | Split on `##` section boundaries | Preserves structure | Requires structured docs |
| **Sentence** | Split by sentences with overlap | Good for dense text | Many small chunks |

### Document Characteristics

GoldenPath governance documents (GOV-*, ADR-*, PRD-*) have consistent structure:

```markdown
---
id: GOV-0017
title: TDD and Determinism Policy
relates_to:
  - ADR-0180
---

# TDD and Determinism Policy

## Purpose
This policy ensures...

## Requirements
1. All code must have tests...

## Exceptions
The following are exempt...
```

Key characteristics:
- YAML frontmatter with metadata
- H1 title matching frontmatter
- H2 sections with clear semantic boundaries
- Consistent structure across document types

## Decision

### Primary Strategy: Markdown Header Chunking

Split documents on `##` (H2) header boundaries. Each section becomes a chunk with:
- Section content (including the header)
- Parent document metadata (id, title, type)
- Section-specific metadata (header text, header level)

### Implementation

```python
from llama_index.core.node_parser import MarkdownNodeParser

parser = MarkdownNodeParser()
nodes = parser.get_nodes_from_documents(documents)
```

### Chunking Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| **Split boundary** | `##` (H2 headers) | Main section boundaries in governance docs |
| **Include header** | Yes | Provides context for the chunk |
| **Max chunk size** | 1024 tokens | Fits embedding model context (8191 for text-embedding-3-small) |
| **Min chunk size** | 50 tokens | Avoid degenerate tiny chunks |
| **Overlap** | 0 tokens | Sections are self-contained, no overlap needed |

### Fallback: Sentence Splitting for Oversized Sections

If a section exceeds 1024 tokens, apply secondary sentence splitting:

```python
from llama_index.core.node_parser import SentenceSplitter

fallback_splitter = SentenceSplitter(
    chunk_size=1024,
    chunk_overlap=100  # Overlap for continuity
)
```

### Metadata Preservation

Each chunk includes:

```python
{
    "doc_id": "GOV-0017",           # From frontmatter
    "doc_title": "TDD Policy",       # From frontmatter
    "doc_type": "policy",            # From frontmatter
    "section": "Requirements",       # H2 header text
    "header_level": 2,               # Header depth
    "relates_to": ["ADR-0180"],      # From frontmatter
    "chunk_index": 3,                # Position in document
    "file_path": "docs/10-governance/policies/GOV-0017.md"
}
```

### Example Output

**Input:**
```markdown
## Requirements

1. All code changes must have corresponding tests
2. Tests must pass before merge
3. Coverage must not decrease
```

**Output Chunk:**
```json
{
  "text": "## Requirements\n\n1. All code changes must have corresponding tests\n2. Tests must pass before merge\n3. Coverage must not decrease",
  "metadata": {
    "doc_id": "GOV-0017",
    "section": "Requirements",
    "header_level": 2,
    "chunk_index": 2
  }
}
```

## Consequences

### Positive

- **Semantic coherence**: Each chunk is a complete, meaningful unit
- **Structure preservation**: Document hierarchy is maintained
- **Query alignment**: Users naturally ask about "sections" (e.g., "What are the requirements?")
- **Metadata richness**: Section headers provide additional retrieval signals
- **Simplicity**: No ML model needed for chunking

### Negative

- **Dependency on structure**: Requires well-structured markdown documents
- **Variable chunk sizes**: Sections vary in length (mitigated by fallback)
- **H1 handling**: Single H1 title may create small chunk (mitigated by merging with first H2)

### Mitigations

| Risk | Mitigation |
|------|------------|
| Unstructured docs | Governance templates enforce structure |
| Oversized sections | Fallback sentence splitting |
| Tiny H1 chunks | Merge H1 with first H2 section |
| Missing headers | Fallback to recursive splitting |

## Alternatives Considered

### Fixed-Size Chunking (512 tokens)

**Rejected because:**
- Breaks governance content mid-requirement
- Loses section context
- Creates arbitrary boundaries

### Semantic Chunking

**Rejected because:**
- Requires additional ML model inference
- Slower ingestion pipeline
- Unnecessary given document structure

### Sentence-Only Chunking

**Rejected because:**
- Creates too many small chunks
- Loses section-level context
- Increases embedding costs

## Implementation

### Phase 0: Basic Implementation

1. Implement `MarkdownNodeParser` in indexing pipeline
2. Extract frontmatter metadata before parsing
3. Store chunks in ChromaDB with metadata

### Phase 1: Refinements

1. Add H1 + first H2 merge logic
2. Add oversized section fallback
3. Add chunk deduplication

### Phase 2: Optimization

1. Tune chunk size based on RAGAS metrics
2. Add semantic similarity for near-duplicate detection
3. Consider parent-child document chunking

## References

- [PRD-0008: Agentic Graph RAG Pipeline](../20-contracts/prds/PRD-0008-governance-rag-pipeline.md)
- [GOV-0020: Agentic Graph RAG Maturity Model](../10-governance/policies/GOV-0020-rag-maturity-model.md)
- [LlamaIndex MarkdownNodeParser](https://docs.llamaindex.ai/en/stable/module_guides/loading/node_parsers/modules/#markdownnodeparser)
- [Chunking Strategies for LLM Applications](https://www.pinecone.io/learn/chunking-strategies/)

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-28 | Claude Opus 4.5 | Initial creation |
