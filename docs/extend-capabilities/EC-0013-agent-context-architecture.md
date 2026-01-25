---
id: EC-0013-agent-context-architecture
title: 'EC-0013: Universal Agent Context Architecture'
type: enhancement-concept
status: draft
domain: platform-core
owner: platform-team
lifecycle: proposed
exempt: false
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: low
schema_version: 1
relates_to:
  - CLAUDE.md
  - .cursorrules
  - session_capture
supersedes: []
superseded_by: []
tags: [ai, agents, dx, context]
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
