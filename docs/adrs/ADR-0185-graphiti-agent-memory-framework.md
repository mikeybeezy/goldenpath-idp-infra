---
id: ADR-0185-graphiti-agent-memory-framework
title: Graphiti as Agent Memory Framework on Neo4j
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
  - ADR-0184-rag-markdown-header-chunking
  - EC-0013-agent-context-architecture
supersedes: []
superseded_by: []
tags:
  - rag
  - graphiti
  - neo4j
  - agent-memory
  - knowledge-graph
inheritance: {}
supported_until: '2028-01-01'
effective_date: 2026-01-28
review_date: 2026-07-28
---

# ADR-0185: Graphiti as Agent Memory Framework on Neo4j

## Status

**Accepted**

## Context

The Agentic Graph RAG pipeline (PRD-0008) requires persistent agent memory across sessions. Without memory preservation:

1. **Context loss** - Agents forget previous conversations and decisions
2. **Redundant queries** - Same questions answered repeatedly
3. **No temporal awareness** - Cannot track when facts changed
4. **Manual entity management** - Relationships must be explicitly coded

### The Agent Memory Problem

```
Session 1:
  User: "What depends on GOV-0017?"
  Agent: [Analyzes, finds ADR-0180, PRD-0008]

Session 2 (new context):
  User: "What else depends on GOV-0017?"
  Agent: [No memory of Session 1, starts from scratch]
```

### Options Considered

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **Raw Neo4j** | Manual Cypher queries | Full control | No temporal awareness, manual entity extraction |
| **LangGraph Memory** | LangChain memory layer | Easy integration | Limited graph capabilities |
| **Graphiti on Neo4j** | Zep's temporal knowledge graph | Agent-native, temporal, auto-extraction | Additional dependency |
| **Custom solution** | Build our own | Tailored | Significant engineering effort |

## Decision

Adopt **Graphiti** as the agent memory framework, running on **Neo4j** as the storage backend.

### Architecture

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

### Why Graphiti

| Capability | How Graphiti Helps |
|------------|-------------------|
| **Entity extraction** | Automatically extracts entities from conversations |
| **Relationship detection** | Identifies relationships without explicit coding |
| **Temporal awareness** | Tracks when facts were learned and changed |
| **Episode management** | Groups related interactions into episodes |
| **Deduplication** | Merges duplicate entities automatically |
| **Neo4j native** | Uses Neo4j for storage, leveraging graph capabilities |

### Memory Preservation Example

```python
from graphiti_core import Graphiti

# Initialize with Neo4j backend
graphiti = Graphiti(
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="..."
)

# Session 1: Agent learns facts
await graphiti.add_episode(
    name="governance-analysis-001",
    episode_body="""
    User asked about GOV-0017 dependencies.
    Found that ADR-0180 implements GOV-0017.
    PRD-0008 also relates to GOV-0017.
    User confirmed this analysis was helpful.
    """,
    source_description="agent-session"
)

# Session 2: Agent remembers
results = await graphiti.search(
    query="What do we know about GOV-0017?",
    num_results=10
)
# Returns: ADR-0180 implements it, PRD-0008 relates to it,
#          user found previous analysis helpful
```

### Integration with Existing Stack

| Component | Role | Integration |
|-----------|------|-------------|
| **ChromaDB** | Vector similarity search | Retrieves relevant chunks |
| **Graphiti** | Agent memory + relationships | Stores facts, entities, episodes |
| **Neo4j** | Graph storage backend | Graphiti's persistence layer |
| **Claude** | LLM for extraction + generation | Graphiti uses for entity extraction |

### Phase Implementation

| Phase | Graphiti Scope |
|-------|----------------|
| **0** | No Graphiti (JSON stub for relationships) |
| **1** | **Graphiti + Neo4j** for basic memory |
| **2** | Graphiti episodes for multi-session context |
| **3+** | Full temporal reasoning, fact evolution |

## Consequences

### Positive

- **Memory persistence** - Agents remember across sessions
- **Temporal awareness** - Track when facts changed
- **Automatic entity extraction** - No manual relationship coding
- **Neo4j foundation** - Graph queries still available
- **Agent-native design** - Built for LLM agent use cases

### Negative

- **Additional dependency** - Graphiti library to manage
- **Neo4j requirement** - Must run Neo4j instance
- **LLM costs** - Entity extraction uses LLM calls
- **Learning curve** - New API to learn

### Mitigations

| Risk | Mitigation |
|------|------------|
| Dependency risk | Graphiti is open source, can fork if needed |
| Neo4j complexity | Use Neo4j AuraDB (managed) for production |
| LLM costs | Batch entity extraction, cache results |
| Learning curve | Start with simple episodes, expand gradually |

## Implementation

### Phase 1 Tasks

1. **Set up Neo4j** (local Docker for dev, AuraDB for prod)
2. **Install Graphiti** (`pip install graphiti-core`)
3. **Create memory service** wrapper for agent use
4. **Index governance docs** as initial knowledge
5. **Add episode capture** for agent sessions

### Configuration

```yaml
# config/graphiti.yaml
neo4j:
  uri: bolt://localhost:7687
  database: governance

graphiti:
  llm_model: claude-sonnet-4-20250514
  embedding_model: text-embedding-3-small

episodes:
  default_source: agent-session
  retention_days: 365
```

### Directory Structure

```
scripts/
  rag/
    graphiti_client.py    # Graphiti wrapper
    memory_service.py     # Agent memory interface
    episode_capture.py    # Session recording

config/
  graphiti.yaml           # Graphiti configuration
```

## References

- [Graphiti: Building Temporal Knowledge Graphs](https://neo4j.com/blog/developer/graphiti-knowledge-graph-memory/)
- [Graphiti GitHub](https://github.com/getzep/graphiti)
- [PRD-0008: Agentic Graph RAG Pipeline](../20-contracts/prds/PRD-0008-governance-rag-pipeline.md)
- [EC-0013: Agent Context Architecture](../extend-capabilities/EC-0013-agent-context-architecture.md)

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-28 | Claude Opus 4.5 | Initial creation |
