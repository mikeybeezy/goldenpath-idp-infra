---
id: ADR-0186-llamaindex-retrieval-layer
title: LlamaIndex as Retrieval Layer for RAG Pipeline
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
  - ADR-0184-rag-markdown-header-chunking
  - ADR-0185-graphiti-agent-memory-framework
  - PRD-0008-governance-rag-pipeline
  - GOV-0020-rag-maturity-model
supersedes: []
superseded_by: []
tags:
  - rag
  - llm
  - retrieval
  - llamaindex
inheritance: {}
supported_until: '2028-01-01'
effective_date: 2026-01-28
review_date: 2026-07-28
---

# ADR-0186: LlamaIndex as Retrieval Layer for RAG Pipeline

## Status

**Accepted**

## Context

The Agentic Graph RAG pipeline (PRD-0008) requires a retrieval layer to query indexed governance documents. During Phase 0 implementation, we built:

- `loader.py` (SCRIPT-0070) - Custom document loader with YAML frontmatter extraction
- `chunker.py` (SCRIPT-0071) - Custom H2 header-based chunking per ADR-0184
- `indexer.py` (SCRIPT-0072) - ChromaDB vector indexing

The question arose: should we also use LlamaIndex for document loading and chunking, or only for retrieval?

### Custom vs LlamaIndex Components

| Component | Custom Implementation | LlamaIndex Alternative |
|-----------|----------------------|------------------------|
| **Loader** | Extracts YAML frontmatter as structured metadata | Generic markdown loaders, no frontmatter support |
| **Chunker** | H2 header splitting, preserves section names | MarkdownNodeParser, more generic |
| **Indexer** | Direct ChromaDB integration | VectorStoreIndex with ChromaDB backend |
| **Retriever** | Not yet implemented | QueryEngine with hybrid search, reranking |

### Retrieval Capabilities Needed

| Capability | ChromaDB Direct | LlamaIndex |
|------------|-----------------|------------|
| Semantic search (vector similarity) | ✅ | ✅ |
| Metadata filtering | ✅ | ✅ |
| Keyword search (BM25) | ⚠️ Limited | ✅ Built-in hybrid |
| Query rewriting | ❌ | ✅ |
| Response synthesis | ❌ | ✅ |
| Reranking | ❌ | ✅ |

## Decision

**Use LlamaIndex ONLY for the retrieval layer**, keeping custom loader/chunker implementations.

### Architecture

```
Custom Code                    LlamaIndex
───────────                    ──────────
loader.py  ──┐
             ├──► Chunks ──► VectorStoreIndex ──► QueryEngine
chunker.py ──┘              (ChromaDB backend)   (hybrid search)
             │
indexer.py ──┘
```

### Rationale

1. **Custom ingestion is governance-specific**: Our loader extracts YAML frontmatter into structured metadata (`id`, `title`, `relates_to`, `type`). LlamaIndex's generic loaders don't support this format.

2. **Custom chunker is tested and locked**: The H2 header chunker has 19 unit tests and golden output tests. It handles edge cases like fenced code blocks. Replacing it would lose this test coverage.

3. **LlamaIndex excels at retrieval**: The retrieval layer is where LlamaIndex provides the most value:
   - Hybrid search (BM25 + vector) without additional dependencies
   - Query rewriting for better semantic matching
   - Response synthesis for RAG-style answers
   - Easy swap of embedding models

4. **Minimal coupling**: By using LlamaIndex only for retrieval, we maintain flexibility. If LlamaIndex changes or we need to swap it, only the retriever needs modification.

## Consequences

### Positive

- Get hybrid search without implementing BM25 ourselves
- Query rewriting improves retrieval quality
- Response synthesis available for RAG answers
- Custom ingestion preserves governance-specific metadata
- Existing tests remain valid

### Negative

- Additional dependency (`llama-index`, `llama-index-vector-stores-chroma`)
- Need to convert our `Chunk` objects to LlamaIndex `Document` nodes
- Two abstraction layers (our chunker → LlamaIndex nodes)

### Neutral

- ChromaDB remains the vector store (already a dependency)
- Embedding model unchanged (ChromaDB default or LlamaIndex-configured)

## Implementation

### Dependencies

```
llama-index
llama-index-vector-stores-chroma
```

### Retriever Interface

```python
from scripts.rag.retriever import GovernanceRetriever

retriever = GovernanceRetriever()

# Semantic search
results = retriever.query("What are the TDD requirements?")

# With metadata filter
results = retriever.query(
    "coverage targets",
    filters={"doc_type": "governance"}
)

# Hybrid search (BM25 + vector)
results = retriever.query(
    "pytest coverage",
    mode="hybrid"
)
```

### Chunk to Node Conversion

```python
from llama_index.core.schema import TextNode

def chunk_to_node(chunk: Chunk) -> TextNode:
    return TextNode(
        text=chunk.text,
        metadata=chunk.metadata,
        id_=f"{chunk.metadata['doc_id']}_{chunk.metadata['chunk_index']}"
    )
```

## Alternatives Considered

### 1. Pure ChromaDB (No LlamaIndex)

Build retriever using only ChromaDB's query API.

**Rejected because:** Would need to implement BM25, query rewriting, and response synthesis from scratch.

### 2. Full LlamaIndex Stack

Replace custom loader/chunker with LlamaIndex equivalents.

**Rejected because:** LlamaIndex's generic loaders don't extract our YAML frontmatter format. Would lose 55 tests and governance-specific metadata handling.

### 3. LangChain Instead

Use LangChain for retrieval layer.

**Rejected because:** LlamaIndex has better native ChromaDB integration and simpler API for our use case. LangChain adds more abstraction than needed.

## References

- [PRD-0008: Agentic Graph RAG Pipeline](../20-contracts/prds/PRD-0008-governance-rag-pipeline.md)
- [ADR-0184: RAG Markdown Header Chunking](./ADR-0184-rag-markdown-header-chunking.md)
- [ADR-0185: Graphiti Agent Memory Framework](./ADR-0185-graphiti-agent-memory-framework.md)
- [LlamaIndex Documentation](https://docs.llamaindex.ai/)
- [LlamaIndex ChromaDB Integration](https://docs.llamaindex.ai/en/stable/examples/vector_stores/ChromaIndexDemo/)
