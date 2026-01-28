---
id: EC-0013-agent-context-architecture
title: 'EC-0013: Universal Agent Context Architecture'
type: enhancement-concept
status: draft
lifecycle: proposed
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: low
relates_to:
  - CLAUDE.md
  - .cursorrules
  - session_capture
tags:
  - ai
  - agents
  - dx
  - context
version: '1.0'
---

# EC-0013: Universal Agent Context Architecture

## Problem Statement

AI agents (Claude Code, Cursor, Copilot, Codex, etc.) lack a universal mechanism for bootstrapping context when joining a session. Each tool has its own convention:

| Agent | Entry Point | Auto-read |
|-------|-------------|-----------|
| Claude Code | `CLAUDE.md` | Yes |
| Cursor | `.cursorrules` | Yes |
| GitHub Copilot | `.github/copilot-instructions.md` | Yes |
| Aider | `CONVENTIONS.md` | Partial |
| Codex (OpenAI) | None | No |
| Generic LLMs | None | No |

This creates:
1. **Duplication** - Same context maintained in multiple files
2. **Cold-start gaps** - Agents without auto-read start blind
3. **Session discontinuity** - Context lost between sessions
4. **Cross-agent inconsistency** - Different agents get different context

## Proposed Solution

### Option A: Inline Headers (Rejected)

Add standardized headers to every file:
```markdown
<!-- AGENT: If onboarding, read docs/AGENT_CONTEXT.md first -->
```

**Problems:**
- Maintenance burden (every file needs header)
- Stale pointers when files rename
- Token bloat (agents read headers everywhere)
- Circular reference risk

### Option B: Centralized Agent Directory (Recommended)

Create a universal `.agent/` directory:

```
.agent/
  README.md              # Universal entry point
  context/
    platform.md          # Core platform architecture
    governance.md        # Scripts, changelogs, certification
    deployment.md        # Build/teardown patterns
    session-current.md   # Symlink to active session capture
  prompts/
    PROMPT-0004.md       # Hotfix policy
    PROMPT-0005.md       # Commit conventions
```

Tool-specific configs become one-line pointers:

```markdown
# CLAUDE.md
Read .agent/README.md before starting any task.
```

```yaml
# .cursorrules
context: Read .agent/README.md first for project conventions.
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Agent Entry                          │
│  (Claude Code / Cursor / Copilot / Codex / Generic)     │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Tool-Specific Config                        │
│  CLAUDE.md / .cursorrules / copilot-instructions.md     │
│                      │                                   │
│         "Read .agent/README.md first"                   │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                 .agent/README.md                         │
│  - Project overview                                      │
│  - Key conventions                                       │
│  - Context file routing by task type                    │
└─────────────────────┬───────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
┌───────────┐  ┌───────────┐  ┌───────────┐
│ platform  │  │governance │  │deployment │
│   .md     │  │   .md     │  │   .md     │
└───────────┘  └───────────┘  └───────────┘
```

## Benefits

| Benefit | Description |
|---------|-------------|
| Single source of truth | One place to maintain agent context |
| Cross-agent compatible | Any agent can be told "read .agent/" |
| Task-appropriate loading | README routes to relevant context |
| Session continuity | `session-current.md` symlink bridges sessions |
| Low maintenance | Add context once, all agents benefit |

## Implementation Plan

### Phase 1: Directory Structure
- [ ] Create `.agent/` directory
- [ ] Create `.agent/README.md` with routing logic
- [ ] Create initial context files (platform, governance, deployment)

### Phase 2: Tool Integration
- [ ] Update `CLAUDE.md` to point to `.agent/`
- [ ] Create `.cursorrules` pointing to `.agent/`
- [ ] Create `.github/copilot-instructions.md` pointing to `.agent/`

### Phase 3: Session Bridge
- [ ] Add `session-current.md` symlink mechanism
- [ ] Update session capture template to support agent handoff

## Open Questions

1. Should `.agent/` be committed or `.gitignore`d?
   - **Recommendation:** Committed (shared context benefits all contributors)

2. How to handle sensitive context (credentials, internal URLs)?
   - **Recommendation:** Separate `.agent/private/` that's gitignored

3. Should context files be auto-generated from existing docs?
   - **Recommendation:** Start manual, automate later if pattern proves valuable

## Decision

**Status:** Awaiting review

**Recommendation:** Implement Option B (Centralized Agent Directory)

---

Proposed by: platform-team
Date: 2026-01-25

---

## Addendum: Relationship to RAG Pipeline (GOV-0020)

*Added: 2026-01-28*

### The Problem EC-0013 Solves That RAG Cannot

During a session building [GOV-0020-rag-maturity-model](../10-governance/policies/GOV-0020-rag-maturity-model.md), an agent made a critical error: inventing fake "VQ-0050" style IDs instead of using the actual VQ classification framework defined in [VQ_PRINCIPLES.MD](../00-foundations/product/VQ_PRINCIPLES.MD).

**Root Cause Analysis:**

```
What happened:
  1. Agent needed to tag deliverables with VQ
  2. Agent didn't know VQ_PRINCIPLES.md existed
  3. Agent didn't know to ask "how does VQ work?"
  4. Agent invented fake VQ IDs

What EC-0013 would have prevented:
  1. Session starts → agent reads .agent/README.md
  2. README says: "For value tracking, read VQ_PRINCIPLES.md first"
  3. Agent would have known the VQ framework BEFORE touching GOV-0020
  4. No fake IDs
```

### EC-0013 is a Prerequisite for RAG, Not a Complement

| Layer | Purpose | Enforcement |
|-------|---------|-------------|
| **EC-0013** | "Read these BEFORE doing anything" | Mandatory bootstrap |
| **RAG** | "Search these WHEN you need answers" | On-demand lookup |

**RAG requires the agent to *know to ask*.** An agent won't query RAG for "how does VQ work?" if it doesn't know VQ exists. EC-0013 forces awareness of core frameworks before any work begins.

### Revised Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AGENT KNOWLEDGE FLOW                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Session Start                                              │
│       │                                                     │
│       ▼                                                     │
│  .agent/README.md (MANDATORY - EC-0013)                     │
│  ├── "Read VQ_PRINCIPLES.md for value tracking"             │
│  ├── "Read GOV-0017 for TDD requirements"                   │
│  ├── "Read CLAUDE.md for agent protocols"                   │
│  └── "Use RAG for everything else"                          │
│       │                                                     │
│       ▼                                                     │
│  During Task                                                │
│       │                                                     │
│       ├── Agent knows core docs exist (EC-0013)             │
│       │                                                     │
│       └── Agent queries RAG for specifics (GOV-0020)        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Key Insight

**EC-0013 = Guardrails (what agents MUST know)**
**RAG = Search (what agents CAN find)**

Without EC-0013, agents don't know what they don't know. RAG helps find answers, but only if agents know to ask the right questions.

### Updated Relates To

This EC now relates to:
- [GOV-0020-rag-maturity-model](../10-governance/policies/GOV-0020-rag-maturity-model.md) - RAG maturity framework
- [PRD-0008-governance-rag-pipeline](../20-contracts/prds/PRD-0008-governance-rag-pipeline.md) - RAG implementation PRD

### Recommendation

Implement EC-0013 **before** or **in parallel with** RAG Phase 0. The `.agent/README.md` should include:

```markdown
## Before Any Task

1. **Value Tracking:** Read [VQ_PRINCIPLES.md](../00-foundations/product/VQ_PRINCIPLES.MD)
2. **Testing Policy:** Read [GOV-0017](../10-governance/policies/GOV-0017-tdd-and-determinism.md)
3. **Agent Protocols:** Read [CLAUDE.md](../../CLAUDE.md)

## During Task

For governance questions, use RAG: `gov-rag ask "your question"`
```

This ensures agents have foundational context before relying on RAG for dynamic lookup.
