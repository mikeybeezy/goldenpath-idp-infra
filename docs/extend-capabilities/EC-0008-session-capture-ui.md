<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: EC-0008-session-capture-ui
title: Session Capture and Summary UI
type: extension-capability
status: proposed
domain: catalog
relates_to:
  - ADR-0167
  - EC-0009-goldenpath-cli
  - EC-0010-agent-pairing-mode
  - agent_session_summary
  - session_capture_template
priority: low
vq_class: 🟡 HV/LQ
estimated_roi: $5K/year
effort_estimate: 2-8 hours (depending on approach)
---

## Executive Summary

A lightweight UI layer to browse, search, and visualize session captures and agent summaries. Session captures document multi-agent collaboration, decisions made, and artifacts touched - currently stored as markdown files with YAML frontmatter.

**Key Benefits**:
- Team visibility into agent work history
- Pattern discovery (common decisions, frequently touched files)
- Audit trail for platform governance work
- Better navigation than raw file browsing

**Estimated ROI**: $5K/year from reduced context-switching when reviewing agent work and faster onboarding for new team members understanding platform decisions.

## Problem Statement

### Current State

```text
Session Capture Discovery Today:
1. Open session_capture/ directory
2. Browse by filename (date-based)
3. Open each .md file individually
4. No search, no filtering, no timeline view
5. No aggregated view of patterns
```

### Pain Points

1. **Discovery Friction**: Finding relevant sessions requires manual file browsing
2. **No Search**: Cannot search across session content or metadata
3. **No Timeline**: Cannot see work progression over time
4. **No Aggregation**: Cannot see which files/ADRs are most frequently touched
5. **Context Loss**: Team members not in session miss the "why" behind changes

### Current Metrics

| Metric | Current State |
|--------|---------------|
| Session captures | 20+ files |
| Agent summaries | 1 aggregate file |
| Search capability | None (grep only) |
| Navigation | Manual file browsing |

## Proposed Solution

### Tiered Implementation Options

#### Option 1: TechDocs Indexing (Minimal - 30 min)

Add `session_capture/` and `session_summary/` to Backstage TechDocs catalog.

**Pros**: Zero new code, immediate search via Backstage
**Cons**: No custom UI, limited filtering

```yaml
# catalog-info.yaml addition
metadata:
  annotations:
    backstage.io/techdocs-ref: dir:session_capture
```

#### Option 2: Static Site Generator (Simple - 2-3 hours)

Use Eleventy/Astro to generate a browsable index with:
- Timeline view
- Tag filtering
- Full-text search
- Agent attribution

**Pros**: Fast to build, deployable anywhere
**Cons**: Separate from Backstage, no live updates

#### Option 3: Backstage Plugin (Integrated - 1-2 days)

Custom Backstage plugin providing:
- Session timeline component
- Agent activity dashboard
- File impact visualization
- Decision search

**Pros**: Integrated experience, real-time updates
**Cons**: More effort, Backstage dependency

### Recommended Approach

**Start with Option 1** (TechDocs indexing) for immediate value, then evaluate need for Option 3 based on usage patterns.

## Data Model

Session captures already have structured frontmatter:

```yaml
# Existing session capture structure
id: session_capture_YYYY_MM_DD_topic
title: Session Capture - Topic
type: documentation
status: active
relates_to:
  - ADR-xxxx
  - CL-xxxx
```

Content sections:
- Session metadata (Agent, Date, Branch)
- Scope
- Work Summary
- Artifacts Touched (Modified/Added/Removed/Referenced)
- Validation
- Current State / Follow-ups
- Updates (append-only log)
- Review/Validation Appendix

## Implementation Path

### Phase 1: TechDocs Integration (P3)

1. Add session_capture to TechDocs catalog
2. Verify search works across sessions
3. Add navigation links from main docs

### Phase 2: Static Index (P3 - if needed)

1. Generate session index page
2. Add tag cloud for common topics
3. Create agent activity summary

### Phase 3: Backstage Plugin (P4 - if demand exists)

1. Design plugin architecture
2. Implement timeline component
3. Add search and filtering
4. Deploy to Backstage

## Success Criteria

| Metric | Target |
|--------|--------|
| Session discovery time | < 30 seconds to find relevant session |
| Search coverage | 100% of session content searchable |
| Team adoption | Used by 2+ team members monthly |

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Low usage | Low | Start minimal, expand only if needed |
| Maintenance burden | Low | Use existing tools (TechDocs, static gen) |
| Scope creep | Medium | Strict phased approach |

## Decision

**Status**: Proposed (P3)

This is a "nice to have" capability. The session capture format already serves its primary purpose (agent context preservation). A UI adds discoverability but doesn't unlock new capability.

**Recommendation**: Implement Option 1 (TechDocs) when convenient. Defer Options 2-3 unless explicit demand emerges.

---

## References

- [ADR-0167: Session Capture Guardrail](../adrs/ADR-0167-session-capture-guardrail.md)
- [Session Capture Template](../../session_capture/session_capture_template.md)
- [Agent Session Summary](../../session_summary/agent_session_summary.md)

Signed: platform-team (2026-01-20)
