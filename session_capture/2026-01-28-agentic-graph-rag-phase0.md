---
id: 2026-01-28-agentic-graph-rag-phase0
title: 'Session Capture: Agentic Graph RAG Phase 0 TDD Implementation'
type: documentation
domain: platform-core
owner: platform-team
lifecycle: active
status: active
schema_version: 1
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - PRD-0008-governance-rag-pipeline
  - GOV-0020-rag-maturity-model
  - ADR-0184-rag-markdown-header-chunking
  - ADR-0185-graphiti-agent-memory-framework
  - GOV-0017-tdd-and-determinism
  - ADR-0182-tdd-philosophy
---

# Session Capture: Agentic Graph RAG Phase 0 TDD Implementation

## Session Metadata

**Agent:** Claude Opus 4.5
**Date:** 2026-01-28
**Timestamp:** 2026-01-28T09:00:00Z
**Branch:** feature/phase0-rag-implementation

## Scope

- Understand Phase 0 Agentic Graph RAG architecture
- Create ADRs for chunking strategy (ADR-0184) and Graphiti adoption (ADR-0185)
- Apply TDD governance principles (GOV-0017) to RAG implementation
- Implement test-first loader and chunker components

## Architecture Decisions

### ADR-0184: RAG Markdown Header Chunking Strategy

**Decision:** Split governance documents on `##` (H2) header boundaries.

**Rationale:**
- Governance docs have consistent H2 section structure
- Preserves semantic coherence (each chunk is a complete section)
- Aligns with how users query ("What are the requirements?")
- No ML model needed for chunking

**Parameters:**
| Parameter | Value |
|-----------|-------|
| Split boundary | `##` (H2 headers) |
| Max chunk size | 1024 tokens |
| Min chunk size | 50 tokens |
| Overlap | 0 tokens (sections are self-contained) |

### ADR-0185: Graphiti as Agent Memory Framework

**Decision:** Adopt Graphiti for agent memory, running ON Neo4j as storage backend.

**Key Insight:** Graphiti is not an alternative to Neo4j - it's built on Neo4j. From the Neo4j blog:

> "Graphiti is a Python library that builds and queries a temporal knowledge graph from unstructured data, using Neo4j as its storage backend."

**Architecture:**
```
Agent Layer (Claude)
       │
       ├──► ChromaDB (Vector similarity)
       │
       └──► Graphiti (Agent memory)
                │
                └──► Neo4j (Graph storage)
```

**Phase Implementation:**
| Phase | Graphiti Scope |
|-------|----------------|
| 0 | No Graphiti (JSON stub for relationships) |
| 1 | Graphiti + Neo4j for basic memory |
| 2 | Episodes for multi-session context |
| 3+ | Full temporal reasoning |

## TDD Influence on Implementation

### GOV-0017 Core Principle Applied

> "Nothing that generates infrastructure, parses config, or emits scaffolds may change without tests."

RAG components are **determinism-critical**:

| Component | GOV-0017 Category | Why Critical |
|-----------|-------------------|--------------|
| `loader.py` | Parser | Incorrect parsing corrupts chunks |
| `chunker.py` | Generator | Output drift breaks embeddings |
| `indexer.py` | Metadata Engine | Metadata is source of truth |

### Tiered Test Strategy

**Tier 1: Unit Tests (Required)**
- `test_loader.py` - frontmatter extraction, content separation
- `test_chunker.py` - H2 splitting, metadata preservation

**Tier 2: Golden Output Tests (Required for Chunker)**
- Chunker generates deterministic chunk payloads; golden tests serialize chunks to JSON
- Blessed outputs in `tests/golden/fixtures/expected/chunks/`
- Golden files require human approval before blessing

### Test-First Workflow

```
1. Write test_loader.py    → tests fail (RED)
2. Implement loader.py     → tests pass (GREEN)
3. Write test_chunker.py   → tests fail (RED)
4. Implement chunker.py    → tests pass (GREEN)
5. Bless golden outputs    → human approval
6. Refactor with confidence
```

## Phase 0 Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Vector Store** | ChromaDB | Local, no infra needed, pip install |
| **Graph Store** | JSON stub | Placeholder for Phase 1 Neo4j |
| **Indexing** | LlamaIndex | Document loading, chunking, embedding |
| **Evaluation** | RAGAS | Quality metrics baseline |
| **LLM** | Claude | Generation + Graphiti entity extraction (Phase 1) |

### Why ChromaDB for Phase 0

1. **Zero infrastructure** - No Docker, no cloud service
2. **Notebook friendly** - Works in Jupyter/Colab
3. **Pip install** - `pip install chromadb`
4. **Persistent** - SQLite backend, survives restarts
5. **Migration path** - Easy to swap for Pinecone/Weaviate later

## Files Created

### ADRs

| File | Purpose |
|------|---------|
| `docs/adrs/ADR-0184-rag-markdown-header-chunking.md` | Chunking strategy decision |
| `docs/adrs/ADR-0185-graphiti-agent-memory-framework.md` | Graphiti + Neo4j adoption |

### Implementation (TDD)

| File | Purpose |
|------|---------|
| `scripts/rag/__init__.py` | Package init |
| `scripts/rag/loader.py` | Document loading + frontmatter extraction |
| `scripts/rag/chunker.py` | Markdown H2 header chunking |
| `tests/unit/test_loader.py` | Loader unit tests |
| `tests/unit/test_chunker.py` | Chunker unit tests |
| `tests/golden/fixtures/inputs/GOV-0017-sample.md` | Golden test input |
| `tests/golden/test_chunker_golden.py` | Golden output tests |
| `tests/golden/fixtures/expected/chunks/GOV-0017/chunks.json` | Blessed chunk outputs |

## Architecture Diagram (Final)

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENTIC GRAPH RAG STACK                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                      AGENT LAYER                         │   │
│   │                  (Claude + Tools)                        │   │
│   └──────────────────────────┬──────────────────────────────┘   │
│                              │                                   │
│              ┌───────────────┼───────────────┐                  │
│              │               │               │                  │
│              ▼               ▼               ▼                  │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│   │   ChromaDB   │  │   Graphiti   │  │    Tools     │         │
│   │  (Vectors)   │  │  (Memory)    │  │   (Actions)  │         │
│   └──────────────┘  └──────┬───────┘  └──────────────┘         │
│                            │                                    │
│                            │ stores in                          │
│                            ▼                                    │
│                     ┌──────────────┐                            │
│                     │    Neo4j     │                            │
│                     │   (Graph)    │                            │
│                     └──────────────┘                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Key Insight:** ChromaDB and Neo4j are PARALLEL paths to the Retriever. They don't talk to each other - both feed the agent independently:
- ChromaDB: "What documents are semantically similar to this query?"
- Neo4j: "What entities relate to this document?"

## Lessons Learned

1. **Graphiti complements Neo4j** - It's not a replacement, it's built ON Neo4j
2. **Embedding model consumes TEXT** - Not coupled to Vector DB, it's a service
3. **TDD applies to RAG** - Chunker is a generator, needs golden output tests
4. **Phase 0 is minimal** - ChromaDB + JSON stub, no graph until Phase 1

## Next Steps

1. Add indexer.py for ChromaDB integration
2. Add retriever.py for query interface
3. Create first Jupyter notebook for experimentation

## Follow-Up Work Completed (Post-Session)

**Date:** 2026-01-28

### Hardening

- Added a fenced-code guard so `##` inside ```/~~~ blocks does not create new chunks.
- Added a unit test to lock the fenced-code behavior.

### Golden Tests

- Added `tests/golden/test_chunker_golden.py` for deterministic chunk payload snapshots.
- Added blessed outputs for GOV-0017 in `tests/golden/fixtures/expected/chunks/GOV-0017/chunks.json`.

### Tests Run

- `pytest tests/golden/test_chunker_golden.py -q` (PASS)
- `pytest tests/unit/test_chunker.py -q` (PASS)
- `pytest tests/unit -q` (PASS)

### Review Request

Please have Claude review the fenced-code guard logic and the golden snapshot for GOV-0017.

## References

- [PRD-0008: Agentic Graph RAG Pipeline](../docs/20-contracts/prds/PRD-0008-governance-rag-pipeline.md)
- [GOV-0020: RAG Maturity Model](../docs/10-governance/policies/GOV-0020-rag-maturity-model.md)
- [ADR-0184: RAG Markdown Header Chunking](../docs/adrs/ADR-0184-rag-markdown-header-chunking.md)
- [ADR-0185: Graphiti Agent Memory Framework](../docs/adrs/ADR-0185-graphiti-agent-memory-framework.md)
- [GOV-0017: TDD and Determinism Policy](../docs/10-governance/policies/GOV-0017-tdd-and-determinism.md)
- [Graphiti: Building Temporal Knowledge Graphs](https://neo4j.com/blog/developer/graphiti-knowledge-graph-memory/)

---

## Update - 2026-01-28T10:30:00Z

### TDD Implementation Complete

Successfully implemented loader and chunker with test-first approach:

**Test Results:**

```text
33 tests passed in 0.08s
- tests/unit/test_loader.py: 15 passed
- tests/unit/test_chunker.py: 18 passed
```

**Files Created:**

| File | SCRIPT ID | Purpose |
|------|-----------|---------|
| `scripts/rag/__init__.py` | - | Package init |
| `scripts/rag/loader.py` | SCRIPT-0070 | Document loading + frontmatter extraction |
| `scripts/rag/chunker.py` | SCRIPT-0071 | Markdown H2 header chunking |
| `tests/unit/test_loader.py` | - | 15 unit tests for loader |
| `tests/unit/test_chunker.py` | - | 18 unit tests for chunker |
| `tests/golden/fixtures/inputs/GOV-0017-sample.md` | - | Golden test input fixture |

**Commit:**

```text
68f9f047 feat(rag): add Phase 0 loader and chunker with TDD tests
```

**Branch:** `feature/phase0-rag-implementation`

### TDD Compliance Verified

Per GOV-0017 requirements:

| Requirement                        | Status                     |
| ---------------------------------- | -------------------------- |
| Tests written before implementation | ✅ RED → GREEN workflow    |
| Loader tests (parser)              | ✅ 15 tests                |
| Chunker tests (generator)          | ✅ 18 tests                |
| Pre-commit hooks pass              | ✅ All hooks passed        |
| Script metadata headers            | ✅ SCRIPT-0070, SCRIPT-0071 |

### Outstanding (Phase 0 Continuation)

- [x] Add `indexer.py` with ChromaDB integration (TDD)
- [ ] Add `retriever.py` with query interface (TDD)
- [x] Bless golden output fixtures for chunker
- [x] Add `chromadb` to requirements.txt
- [ ] Create first Jupyter notebook after core scripts complete

---

## Update - 2026-01-28T14:00:00Z

### Indexer Implementation Complete

Successfully implemented ChromaDB indexer with TDD approach:

**Test Results:**

```text
102 unit tests passed
- tests/unit/test_loader.py: 15 passed
- tests/unit/test_chunker.py: 19 passed
- tests/unit/test_indexer.py: 20 passed
```

**Files Created:**

| File                         | SCRIPT ID   | Purpose                     |
|------------------------------|-------------|-----------------------------|
| `scripts/rag/indexer.py`     | SCRIPT-0072 | ChromaDB vector indexing    |
| `tests/unit/test_indexer.py` | -           | 20 unit tests for indexer   |

**Indexer Features:**

- `create_collection()` - Create/get ChromaDB collections
- `index_chunks()` - Index chunks with text and metadata
- `GovernanceIndex` - High-level class for governance docs
- Metadata flattening for ChromaDB compatibility
- Unique ID generation (`{doc_id}_{chunk_index}`)

**Commit:**

```text
6dc699d2 feat(rag): add ChromaDB indexer with TDD tests
```

### Dependencies Added

- `chromadb` added to requirements.txt

### Phase 0 Progress

| Component        | Status                    |
|------------------|---------------------------|
| `loader.py`      | ✅ Complete (SCRIPT-0070) |
| `chunker.py`     | ✅ Complete (SCRIPT-0071) |
| `indexer.py`     | ✅ Complete (SCRIPT-0072) |
| `retriever.py`   | ⬜ Next                   |
| Jupyter notebook | ⬜ After retriever        |
