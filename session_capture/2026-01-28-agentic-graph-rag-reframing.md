---
id: session-2026-01-28-agentic-graph-rag-reframing
title: Agentic Graph RAG Documentation Reframing
type: session-capture
date: 2026-01-28
status: completed
relates_to:
  - GOV-0020-rag-maturity-model
  - PRD-0008-governance-rag-pipeline
  - EC-0017-platform-distribution-framework
  - EC-0013-agent-context-architecture
tags:
  - documentation
  - rag
  - agentic
  - graph
  - platform
---

# Session Capture: Agentic Graph RAG Documentation Reframing

## Session Context

**Date:** 2026-01-28
**Participants:** platform-team, Claude Code agent
**Focus:** Reframe RAG documentation to emphasize Agentic Graph RAG architecture

## Problem Statement

The existing RAG documentation (GOV-0020, PRD-0008) undersold the architectural vision:

| Document | Previous Title | Issue |
|----------|----------------|-------|
| GOV-0020 | "RAG Maturity Model" | Didn't mention Agentic or Graph |
| PRD-0008 | "Governance RAG Pipeline" | Sounded like basic RAG |

The architecture is **Agentic Graph RAG from day one** - the knowledge graph and agentic capabilities are foundational, not Phase 1 add-ons.

## Changes Made

### 1. GOV-0020 Updates

- **Title:** Changed to "Agentic Graph RAG Maturity Model"
- **Purpose section:** Enhanced to emphasize three pillars:
  - Knowledge Graph (Neo4j) for entity relationships
  - Agentic Capabilities for autonomous operations
  - RAG for grounded retrieval

### 2. PRD-0008 Updates

- **Title:** Changed to "Agentic Graph RAG Pipeline"
- **Added Vision section:** Explaining graph-first architecture and agentic end-state
- **Added CI/CD Workflows section:** Four workflows for RAG quality:
  - `ci-rag-index.yml` - Index governance docs on merge
  - `ci-rag-quality.yml` - RAGAS metrics quality gate
  - `ci-rag-graph.yml` - Graph sync validation
  - `ci-rag-agent-eval.yml` - Agent evaluation for L3-L4
- **Added Metrics Capture Strategy:** RAGAS metrics + Agent metrics tables
- **Added Definition of Done:** Metrics capture as prerequisite

### 3. EC-0017 Created

New Enhancement Concept document: **GoldenPath Platform Distribution Framework**

Captures strategy for making GoldenPath a reusable, white-label platform:
- Layered distribution model (Instance Data → Config → Framework → Infrastructure)
- Configuration abstraction with `organization.yaml`
- RAG framework packaging
- Bootstrap process for new organizations

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| Graph-first from Phase 0 | Neo4j captures relationships that pure vector RAG cannot |
| RAGAS metrics as prerequisite | Quality must be quantified before any phase is complete |
| Agentic capabilities as end-state | L3-L4 agents orchestrate tools, not just retrieve text |
| Platform distribution model | Enable other orgs to adopt GoldenPath without forking |

## Files Changed

| File | Change Type |
|------|-------------|
| `docs/10-governance/policies/GOV-0020-rag-maturity-model.md` | Modified (title + purpose) |
| `docs/20-contracts/prds/PRD-0008-governance-rag-pipeline.md` | Modified (title + vision + CI/CD + metrics) |
| `docs/20-contracts/prds/00_INDEX.md` | Modified (PRD-0008 description) |
| `docs/extend-capabilities/EC-0017-platform-distribution-framework.md` | Created |

## Value Delivered

- Documentation now accurately reflects the Agentic Graph RAG vision
- CI/CD workflow patterns defined for RAG quality gates
- Platform distribution strategy documented for future commercialization
- Metrics capture embedded as prerequisite to Definition of Done

## Next Steps

1. Implement RAG Phase 0 (CLI spike with RAGAS baseline)
2. Implement EC-0013 (Agent Context Architecture) in parallel
3. Begin EC-0017 Phase 1 (Framework extraction) when ready to distribute

## Related PRs

- PR #311: docs: Agentic Graph RAG reframing and platform distribution framework
