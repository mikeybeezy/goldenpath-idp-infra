---
id: PRD-0010-governance-rag-mcp-server
title: 'PRD-0010: Governance RAG MCP Server'
type: documentation
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - PRD-0008-governance-rag-pipeline
  - ADR-0185-graphiti-temporal-memory
  - GOV-0020-rag-maturity-model
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# PRD-0010: Governance RAG MCP Server

Status: draft
Owner: platform-team
Date: 2026-01-29

## Problem Statement

The Governance RAG pipeline (PRD-0008) provides vector search over 690+ governance documents via CLI. However, AI agents (Claude Code, LangChain agents, custom orchestrators) cannot programmatically access this knowledge without manual copy-paste or shell execution.

We need a **Model Context Protocol (MCP) server** that exposes the RAG retriever as a tool, enabling AI agents to automatically query governance documents when answering questions about platform policies, ADRs, PRDs, and runbooks.

## Goals

- Expose `GovernanceRetriever` as an MCP tool callable by Claude Code and other MCP-compatible clients
- Enable AI agents to retrieve governance context automatically during conversations
- Provide structured responses with citations (document ID, file path, relevance score)
- Support additional interfaces (REST API, LangChain tool) for non-MCP agents

## Non-Goals

- Building a full RAG-as-a-Service with authentication and multi-tenancy
- Replacing the CLI interface (MCP complements CLI, not replaces)
- Implementing response generation (retrieval only; synthesis is client responsibility)
- Real-time index updates (index rebuild is a separate concern per PRD-0008)

## Scope

- **MCP Server:** `scripts/rag/mcp_server.py` - primary interface for Claude Code
- **REST API:** `scripts/rag/api_server.py` - universal interface for any agent
- **Tool Adapters:** LangChain, LlamaIndex, OpenAI function schemas
- **Clients:** Claude Code, VS Code extension, LangChain agents, custom orchestrators

## Requirements

### Functional

| ID | Requirement | Priority |
|----|-------------|----------|
| F1 | MCP server exposes `query_governance` tool with question and top_k parameters | P0 |
| F2 | Tool returns structured results: text, metadata (id, file_path, type), score | P0 |
| F3 | REST API endpoint `/query` accepts GET with `q` and `top_k` params | P1 |
| F4 | REST API returns JSON with results array and query metadata | P1 |
| F5 | LangChain Tool wrapper for `GovernanceRetriever` | P2 |
| F6 | OpenAI function schema for GPT-based agents | P2 |
| F7 | Health check endpoint for monitoring | P1 |

### Non-Functional

| ID | Requirement | Priority |
|----|-------------|----------|
| NF1 | Query latency < 500ms for top_k=5 | P0 |
| NF2 | No secrets or credentials required for read-only queries | P0 |
| NF3 | Graceful error handling when index not built | P1 |
| NF4 | Structured logging for query observability | P1 |
| NF5 | Compatible with Python 3.11+ | P0 |

## Proposed Approach (High-Level)

1. **MCP Server** - Implement using `mcp` Python SDK with `@server.tool` decorator
2. **REST API** - FastAPI server with `/query` and `/health` endpoints
3. **Shared Core** - Both interfaces use `GovernanceRetriever` from `scripts/rag/retriever.py`
4. **Tool Adapters** - Thin wrappers that convert retriever output to framework-specific formats
5. **Configuration** - Environment variables for collection name, ChromaDB path

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        AI Agents                                 │
├─────────────┬─────────────┬─────────────┬───────────────────────┤
│ Claude Code │  LangChain  │   Custom    │      VS Code          │
│   (MCP)     │   Agents    │   Agents    │     Extension         │
└──────┬──────┴──────┬──────┴──────┬──────┴───────────┬───────────┘
       │             │             │                   │
       ▼             ▼             ▼                   ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐
│ MCP Server  │ │ LangChain   │ │  REST API   │ │  MCP Server     │
│ (stdio)     │ │    Tool     │ │  (FastAPI)  │ │  (stdio)        │
└──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └────────┬────────┘
       │               │               │                  │
       └───────────────┴───────────────┴──────────────────┘
                               │
                               ▼
                 ┌─────────────────────────┐
                 │  GovernanceRetriever    │
                 │  (scripts/rag/retriever)│
                 └────────────┬────────────┘
                              │
                              ▼
                 ┌─────────────────────────┐
                 │      ChromaDB           │
                 │   (9,193 chunks)        │
                 └─────────────────────────┘
```

## Implementation

### Phase 1: MCP Server (P0)

**File:** `scripts/rag/mcp_server.py`

```python
#!/usr/bin/env python3
"""
MCP server exposing GovernanceRetriever as a tool for AI agents.
"""
from mcp.server import Server
from mcp.types import Tool, TextContent
from scripts.rag.retriever import GovernanceRetriever

server = Server("governance-rag")
retriever = None

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="query_governance",
            description="Query governance documents (PRDs, ADRs, GOVs, runbooks) for relevant context. Use when answering questions about platform policies, architecture decisions, or operational procedures.",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question to search for in governance documents"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of results to return (default: 5)",
                        "default": 5
                    }
                },
                "required": ["question"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    global retriever
    if retriever is None:
        retriever = GovernanceRetriever()

    if name == "query_governance":
        question = arguments["question"]
        top_k = arguments.get("top_k", 5)

        results = retriever.query(question, top_k=top_k)

        formatted = []
        for r in results:
            formatted.append(
                f"[{r.metadata.get('id', 'unknown')}] ({r.metadata.get('file_path', 'unknown')})\n"
                f"Score: {r.score:.3f}\n"
                f"{r.text[:500]}..."
            )

        return [TextContent(type="text", text="\n\n---\n\n".join(formatted))]

    raise ValueError(f"Unknown tool: {name}")

if __name__ == "__main__":
    import asyncio
    from mcp.server.stdio import stdio_server

    asyncio.run(stdio_server(server))
```

### Phase 2: REST API (P1)

**File:** `scripts/rag/api_server.py`

```python
#!/usr/bin/env python3
"""
REST API server for Governance RAG queries.
"""
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Optional
from scripts.rag.retriever import GovernanceRetriever

app = FastAPI(title="Governance RAG API", version="1.0.0")
retriever = GovernanceRetriever()

class SearchResult(BaseModel):
    text: str
    score: float
    metadata: dict

class QueryResponse(BaseModel):
    query: str
    top_k: int
    results: List[SearchResult]

@app.get("/health")
def health():
    return {"status": "healthy", "index_loaded": retriever is not None}

@app.get("/query", response_model=QueryResponse)
def query(
    q: str = Query(..., description="Question to search"),
    top_k: int = Query(5, ge=1, le=20, description="Number of results")
):
    results = retriever.query(q, top_k=top_k)
    return QueryResponse(
        query=q,
        top_k=top_k,
        results=[
            SearchResult(
                text=r.text,
                score=r.score,
                metadata=r.metadata
            )
            for r in results
        ]
    )
```

### Phase 3: Tool Adapters (P2)

**LangChain Tool:** `scripts/rag/langchain_tool.py`

```python
from langchain.tools import Tool
from scripts.rag.retriever import GovernanceRetriever

def create_governance_tool() -> Tool:
    retriever = GovernanceRetriever()

    def search(query: str) -> str:
        results = retriever.query(query, top_k=5)
        return "\n\n".join([
            f"[{r.metadata.get('id')}] {r.text[:300]}..."
            for r in results
        ])

    return Tool(
        name="query_governance",
        description="Search governance documents for PRDs, ADRs, policies, and runbooks",
        func=search
    )
```

## Configuration

### Claude Code MCP Config

**File:** `.claude/settings.json`

```json
{
  "mcpServers": {
    "governance-rag": {
      "command": "python",
      "args": ["-m", "scripts.rag.mcp_server"],
      "env": {
        "CHROMA_PERSIST_DIR": ".chroma",
        "CHROMA_COLLECTION": "governance_docs"
      }
    }
  }
}
```

### REST API Startup

```bash
# Development
uvicorn scripts.rag.api_server:app --reload --port 8080

# Production
uvicorn scripts.rag.api_server:app --host 0.0.0.0 --port 8080 --workers 2
```

## Guardrails

- **Read-only access:** MCP server and API only perform queries, no write operations
- **No secrets:** ChromaDB index contains only public governance documents
- **Rate limiting:** REST API should implement rate limiting in production
- **Input validation:** Query strings sanitized, top_k bounded (1-20)

## Observability / Audit

- **Logging:** Each query logged with timestamp, question, top_k, result count
- **Metrics:** Query latency, result count distribution, error rate
- **Health endpoint:** `/health` for monitoring and load balancer checks

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| AC1 | MCP server starts and responds to `list_tools` | `python -m scripts.rag.mcp_server` + MCP client test |
| AC2 | `query_governance` returns results with citations | Manual test with Claude Code |
| AC3 | REST API `/query` returns JSON with results | `curl localhost:8080/query?q=TDD` |
| AC4 | Query latency < 500ms for top_k=5 | Load test with 100 queries |
| AC5 | Unit tests pass for MCP server and API | `pytest tests/unit/test_mcp_server.py` |
| AC6 | Integration test: Claude Code queries governance | Manual verification |

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Query latency (p95) | < 500ms | API logs |
| Adoption | 5+ queries/day within 2 weeks | Log analysis |
| Relevance | 80%+ queries return useful results | User feedback |

## Rollout Plan

| Phase | Scope | Timeline |
|-------|-------|----------|
| 1 | MCP server + Claude Code config | Week 1 |
| 2 | REST API + health monitoring | Week 2 |
| 3 | LangChain/OpenAI adapters | Week 3 |
| 4 | Documentation + onboarding guide | Week 4 |

## Open Questions

1. Should the MCP server support filtering by document type (ADR, PRD, GOV)?
2. Should we cache query results for repeated questions?
3. How do we handle index staleness (query returns old content)?
4. Should REST API require authentication for production use?

## Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| mcp | >=1.0.0 | MCP server SDK |
| fastapi | >=0.100.0 | REST API framework |
| uvicorn | >=0.23.0 | ASGI server |
| langchain | >=0.1.0 | LangChain tool wrapper (optional) |

## References

- [PRD-0008: Governance RAG Pipeline](./PRD-0008-governance-rag-pipeline.md)
- [ADR-0185: Graphiti Temporal Memory](../adrs/ADR-0185-graphiti-temporal-memory.md)
- [MCP Specification](https://modelcontextprotocol.io/docs)
- [Claude Code MCP Documentation](https://docs.anthropic.com/claude-code/mcp)

---

## Comments and Feedback

-
