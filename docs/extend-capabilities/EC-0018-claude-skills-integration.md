---
id: EC-0018-claude-skills-integration
title: 'EC-0018: Claude Skills Integration for GoldenPath Platform'
type: enhancement-concept
status: proposed
lifecycle: proposed
risk_profile:
  production_impact: none
  security_risk: low
  coupling_risk: low
relates_to:
  - PRD-0008-governance-rag-pipeline
  - PRD-0010-governance-rag-mcp-server
  - EC-0013-agent-context-architecture
  - GOV-0017-tdd-and-determinism
tags:
  - claude-code
  - skills
  - developer-experience
  - ai-assistance
  - terraform
priority: high
vq_class: HV/HQ
estimated_roi: Developer productivity + governance compliance
effort_estimate: 2-4 weeks
version: '1.0'
---

# EC-0018: Claude Skills Integration for GoldenPath Platform

## Executive Summary

This capability evaluates integrating **Claude Skills** into the GoldenPath platform to provide developers with instant, context-aware guidance on infrastructure patterns and governance policies. Skills are executable documentation that Claude Code loads automatically when relevant - functioning as "always-on" expertise.

**Key Finding:** Claude Skills complement our existing Governance RAG system:
- **Skills** = instant expertise (patterns, best practices) - always loaded
- **RAG** = semantic search (policies, decisions) - on-demand retrieval
- **MCP** = live data (registry lookups, versions) - real-time queries

## Problem Statement

Developers working on GoldenPath projects need to:

1. Follow governance policies (GOV-0017 TDD requirements, naming conventions)
2. Use approved Terraform modules and patterns
3. Maintain consistency across infrastructure code
4. Quickly find relevant documentation

Current gaps:

| Gap | Impact |
|-----|--------|
| No instant policy guidance | Developers must search docs manually |
| Generic AI assistance | Claude lacks org-specific context |
| RAG requires explicit queries | Information not proactively surfaced |
| Terraform expertise fragmented | Best practices not consistently applied |

## Proposed Solution

### Reference Implementation: terraform-skill

**Repository:** [antonbabenko/terraform-skill](https://github.com/antonbabenko/terraform-skill)
**Author:** Anton Babenko (AWS Hero, terraform-aws-modules maintainer)
**Stats:** 829 stars | Apache 2.0 | v1.5.0

The terraform-skill demonstrates a proven pattern:

```
terraform-skill/
├── .claude-plugin/
│   └── marketplace.json     # Plugin metadata (~100 tokens)
├── SKILL.md                 # Core skill (~524 lines, ~4.4K tokens)
├── references/              # Deep-dive content (~26K tokens total)
│   ├── ci-cd-workflows.md
│   ├── code-patterns.md
│   ├── module-patterns.md
│   ├── quick-reference.md
│   ├── security-compliance.md
│   └── testing-frameworks.md
└── README.md
```

### Key Design Patterns

| Pattern | Description | Benefit |
|---------|-------------|---------|
| **Progressive Disclosure** | Metadata scanned first, full skill loaded on activation | 56-70% token reduction |
| **Reference Files** | Detailed content in separate files, loaded on demand | Scales to complex domains |
| **Decision Matrices** | Tables for "when to use X vs Y" decisions | Actionable guidance |
| **DO/DON'T Examples** | Side-by-side code patterns | Visual clarity |

### Token Budget Strategy

- **Metadata:** ~100 tokens - always scanned
- **Core SKILL.md:** ~4,400 tokens - loaded on activation
- **Reference files:** ~26K tokens - loaded only when needed
- **Result:** Typical queries use ~4.5K tokens instead of ~30K

## Architecture Integration

### Hybrid Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Claude Code                          │
├─────────────────────────────────────────────────────────┤
│  Skills (Always Loaded)         │  RAG (On-Demand)      │
│  ─────────────────────          │  ────────────────     │
│  • goldenpath-skill             │  • Governance docs    │
│  • terraform-skill              │  • ADRs, PRDs, GOVs   │
│                                 │  • Session captures   │
│  "Here's the pattern"           │  "GOV-0017 says..."   │
├─────────────────────────────────────────────────────────┤
│                     MCP Servers                         │
│  ─────────────────────────────────────────────────      │
│  • governance-rag-mcp (PRD-0010)                        │
│  • terraform-mcp (registry lookups)                     │
└─────────────────────────────────────────────────────────┘
```

### Capability Matrix

| Capability | Skills | RAG | MCP |
|------------|--------|-----|-----|
| Best practices | Instant | - | - |
| Policy search | - | Semantic | - |
| Graph traversal | - | Neo4j | - |
| Live registry data | - | - | Real-time |
| Version constraints | - | - | Real-time |

### Proposed GoldenPath Skill Structure

```
.claude/skills/goldenpath/
├── SKILL.md                    # Core governance guidance
├── references/
│   ├── terraform-patterns.md   # Our Terraform standards
│   ├── testing-policy.md       # GOV-0017 TDD requirements
│   ├── naming-conventions.md   # Our naming rules
│   └── module-catalog.md       # Approved modules
└── .claude-plugin/
    └── marketplace.json
```

## Strategic Use Cases

### 1. Terraform Module Development

**Trigger:** Developer creates new Terraform module
**Skill Response:** Automatically surfaces:
- Naming conventions from ADR-0042
- Required tags per GOV-0023
- Testing requirements per GOV-0017
- Approved module patterns

### 2. Policy Compliance

**Trigger:** Developer writes infrastructure code
**Skill Response:** Proactively enforces:
- TDD requirements (tests before implementation)
- 60% coverage targets for V1
- Naming and tagging standards

### 3. Quick Reference

**Trigger:** Developer asks "how do I..."
**Skill Response:** Provides decision matrices:
- When to use Terratest vs native tests
- Module hierarchy patterns
- CI/CD workflow templates

### 4. Onboarding

**Trigger:** New developer starts working on platform
**Skill Response:** Contextual guidance:
- Project structure explanation
- Governance framework overview
- Links to detailed RAG queries

### 5. Code Review

**Trigger:** Developer reviews Terraform PR
**Skill Response:** Checklist of:
- Required elements (tags, naming, tests)
- Common anti-patterns to flag
- Security scanning requirements

## Implementation Roadmap

### Phase 1: Quick Wins (1-2 hours)

| Task | Action | Outcome |
|------|--------|---------|
| 1.1 | Install terraform-skill | Immediate Terraform expertise |
| 1.2 | Test with sample queries | Validate activation |
| 1.3 | Document experience | Capture learnings |

### Phase 2: Custom Skill Development (4-8 hours)

| Task | Action | Outcome |
|------|--------|---------|
| 2.1 | Create `.claude/skills/goldenpath/` structure | Foundation |
| 2.2 | Draft SKILL.md with core policies | Initial content |
| 2.3 | Create reference files from GOV/ADR docs | Deep-dive content |
| 2.4 | Test activation and responses | Validation |

### Phase 3: Integration (2-4 hours)

| Task | Action | Outcome |
|------|--------|---------|
| 3.1 | Add skill content to RAG index scope | Searchable |
| 3.2 | Test hybrid queries (skill + RAG) | Unified experience |
| 3.3 | Document usage patterns | Developer guide |

### Phase 4: MCP Alignment (Future)

| Task | Action | Outcome |
|------|--------|---------|
| 4.1 | Align with PRD-0010 MCP server | Tool integration |
| 4.2 | Define tool boundaries (skill vs MCP) | Clear responsibilities |
| 4.3 | Create unified developer experience | Seamless workflow |

## Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Skill content becomes stale | Medium | Medium | Sync with governance doc updates |
| Token budget exceeded | Low | Low | Progressive disclosure pattern |
| Conflicting guidance (skill vs RAG) | Low | Medium | Clear ownership boundaries |
| Developer confusion | Low | Low | Documentation and training |

## Alternatives Considered

### 1. RAG-Only Approach

**Pros:** Single system, already implemented
**Cons:** Requires explicit queries, no proactive guidance
**Decision:** Complement with skills for instant expertise

### 2. Custom MCP Server

**Pros:** Full programmatic control
**Cons:** Higher implementation effort, maintenance burden
**Decision:** Use skills for static content, MCP for dynamic data

### 3. Prompt Engineering in CLAUDE.md

**Pros:** Simple, no new infrastructure
**Cons:** Limited space, no progressive disclosure
**Decision:** Skills provide better structure and scalability

## Cost Analysis

| Item | Cost | Notes |
|------|------|-------|
| Implementation effort | 2-4 weeks | Phase 1-3 |
| Infrastructure | $0 | Uses existing Claude Code |
| Maintenance | 2-4 hours/month | Content updates |
| Token usage | Minimal increase | Progressive disclosure minimizes |

**ROI:** Developer time savings from instant guidance, reduced policy violations, faster onboarding.

## Monitoring & Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Skill activation rate | >50% of Terraform sessions | Claude Code telemetry |
| Policy compliance | Increase in PRs passing first review | Git metrics |
| Developer satisfaction | Positive feedback | Survey |
| Time to first PR (new devs) | 20% reduction | Onboarding metrics |

## Open Questions

1. **Skill Location:** Should skills live in this repo or a separate `goldenpath-skills` repo?

2. **Update Workflow:** How do we keep skill content in sync with governance docs?

3. **Versioning:** Should skills be versioned independently from the platform?

4. **Distribution:** How do developers get/update skills? (marketplace, git clone, npm?)

5. **Testing:** How do we validate skill responses are accurate?

## Recommendation

**Proceed with Phase 1 and 2:**

1. Install `terraform-skill` immediately for Terraform expertise
2. Begin drafting `goldenpath-skill` with core policies
3. Evaluate hybrid architecture after Phase 2 validation

**Rationale:** Quick win from terraform-skill, gradual build of org-specific skill, eventual integration with existing RAG infrastructure per PRD-0008 and PRD-0010.

## References

- [terraform-skill repository](https://github.com/antonbabenko/terraform-skill)
- [terraform-best-practices.com](https://terraform-best-practices.com)
- PRD-0008: Governance RAG Pipeline
- PRD-0010: Governance RAG MCP Server
- GOV-0017: TDD and Determinism Policy
- EC-0013: Agent Context Architecture

---

**Created:** 2026-01-29
**Author:** Claude Opus 4.5
**Status:** Proposed
