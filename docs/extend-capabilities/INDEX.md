---
id: INDEX
title: Extension Capabilities Index
type: index
relates_to:
  - EC-0001-knative-integration
  - EC-0002-shared-parser-library
  - EC-0003-kong-backstage-plugin
  - EC-0004-backstage-copilot-plugin
---

This directory tracks proposed platform capabilities for Golden Path IDP evaluation. Each capability is assigned an EC-XXXX ID and follows a lightweight governance model.

## Purpose

Extension Capabilities (EC) are **decision documents** for evaluating new platform features before committing to implementation. They serve as:

1. **Idea Repository**: Capture potential capabilities without ADR overhead
2. **ROI Analysis**: Document business value before investment
3. **Prioritization Input**: Feed into roadmap planning
4. **Knowledge Base**: Preserve research for future reference

## When to Create an EC Document

Create an EC when:

- Evaluating a new platform capability or technology
- Considering significant architectural additions
- Need structured analysis before ADR commitment
- Want to document "not now" decisions for future reference

Do **NOT** create an EC for:

- Minor feature additions (use standard ADR)
- Bug fixes or maintenance work
- Changes to existing capabilities (use ADR for modifications)

## EC Lifecycle

```text
proposed → validated → accepted → [ADR created] → implemented → [EC archived]
         ↘ rejected → archived
```

### Status Definitions

- **proposed**: Initial idea, awaiting platform team review
- **validated**: Technical feasibility confirmed, ROI calculated
- **accepted**: Approved for roadmap, awaiting implementation planning
- **rejected**: Not pursuing at this time (document preserved for reference)
- **implemented**: Capability deployed, EC archived with reference to ADR

## Document Structure

Each EC document should include:

```yaml
---
id: EC-XXXX
title: Short descriptive title
status: proposed | validated | accepted | rejected | implemented
priority: low | medium | high | critical
vq_class: efficiency | resilience | velocity | governance
estimated_roi: Dollar amount or qualitative value
dependencies: [List of ADRs, existing capabilities]
effort_estimate: Time estimate (weeks/months)
owner: team-name
relates_to: [ADRs, roadmap items]
---
```

### Required Sections

1. **Executive Summary** (2-3 paragraphs)
2. **Problem Statement** (What gap does this fill?)
3. **Proposed Solution** (High-level approach)
4. **Architecture Integration** (How it fits with existing stack)
5. **Strategic Use Cases** (3-5 specific scenarios)
6. **Implementation Roadmap** (Phases with deliverables)
7. **Risk Analysis** (Risks and mitigations)
8. **Alternatives Considered** (Why not other options?)
9. **Cost Analysis** (Infrastructure + operational costs)
10. **Monitoring & Success Metrics** (How to measure value)

## Active Extension Capabilities

|ID|Title|Status|Priority|Estimated ROI|Owner|
|------------------------------------------------------|------------------------------------------------|----------|----------|---------------------|---------------|
|[EC-0001](EC-0001-knative-integration.md)|Knative Integration for Serverless Workloads|proposed|medium|$13K/year|platform-team|
|[EC-0002](EC-0002-shared-parser-library.md)|Shared Parser Library for Requests|proposed|low|Reduced duplication|platform-team|
|[EC-0003](EC-0003-kong-backstage-plugin.md)|Kong Self-Service Backstage Plugin|proposed|medium|$8K/year|platform-team|
|[EC-0004](EC-0004-backstage-copilot-plugin.md)|Backstage AI Copilot Plugin|proposed|medium|$15K/year|platform-team|

## Implemented Capabilities

None yet - capabilities move here after implementation and ADR creation

## Rejected/Archived Capabilities

None yet - rejected ideas preserved for future reference

## Quick Commands

### Create New EC

```bash
# Copy template
cp docs/extend-capabilities/TEMPLATE.md docs/extend-capabilities/EC-XXXX-title.md

# Get next EC number
ls docs/extend-capabilities/EC-*.md | wc -l
```

### Find EC by Topic

```bash
grep -r "kubernetes" docs/extend-capabilities/
```

### List by Status

```bash
grep -h "status:" docs/extend-capabilities/EC-*.md | sort | uniq -c
```

### Generate This Index

```bash
# Automatically regenerate from EC files
python3 scripts/generate_ec_index.py
```

## Integration with Other Docs

### Relationship to ADRs

- **EC**: "Should we build this?" (exploration)
- **ADR**: "How will we build this?" (decision)

**Workflow**: EC-XXXX (validated) → ADR-XXXX (architecture) → Implementation

### Relationship to Roadmap

- Accepted ECs feed into `ROADMAP.md` prioritization
- ROI calculations inform priority levels
- Effort estimates guide sprint planning

### Relationship to Value Quantification

- All ECs must include VQ class (efficiency/resilience/velocity/governance)
- ROI calculations use VQ framework
- Implemented ECs tracked in quarterly VQ reports

## Governance Notes

### Approval Process

1. Create EC with `status: proposed`
2. Platform team review (technical feasibility)
3. Update to `status: validated` with refined estimates
4. Architecture approval → `status: accepted`
5. Create ADR for accepted ECs before implementation
6. Mark `status: implemented` when deployed

### Review Cadence

- Proposed ECs reviewed in weekly platform meetings
- Validated ECs prioritized in quarterly planning
- Rejected ECs reviewed annually for relevance

### Document Ownership

- **Author**: Person who created the EC
- **Owner**: Team responsible for implementation (if accepted)
- Platform team maintains overall EC index

## Questions?

- Slack: #platform-engineering
- Email: <platform-team@goldenpath.io>
- ADR for this system: *TBD - consider ADR-0149 if EC process becomes formal*

---

**Last Updated**: 2026-01-17
**Total ECs**: 4 proposed, 0 validated, 0 accepted, 0 rejected, 0 implemented
