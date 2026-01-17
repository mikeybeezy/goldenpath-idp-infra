---
id: PRD-0000-template
title: 'PRD-0000: <short title>'
type: documentation
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - DOCS_PRDS_README
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# PRD-0000: <short title>

Status: draft
Owner: <team/role>
Date: <YYYY-MM-DD>

## Problem Statement

<What problem are we solving and why now?>

## Goals

- <Goal 1>
- <Goal 2>

## Non-Goals

- <Out of scope 1>
- <Out of scope 2>

## Scope

<Where this applies (envs, products, services) and explicit exclusions.>

## Requirements

### Functional

- <Requirement 1>
- <Requirement 2>

### Non-Functional

- <Requirement 1>
- <Requirement 2>

## Proposed Approach (High-Level)

<1-5 bullets describing the approach without implementation detail.>

## Guardrails

- <Safety or approval constraint>
- <Data/permissions constraint>

## Observability / Audit

- <Logs, metrics, audits, evidence requirements>

## Acceptance Criteria

- <Criteria 1>
- <Criteria 2>

## Success Metrics

- <Metric 1>
- <Metric 2>

## Open Questions

- <Question 1>
- <Question 2>

## References

- <Related ADRs, docs, runbooks>

---

## Comments and Feedback
When providing feedbackk, leave a comment and timestamop your comment.

- <Reviewer name/date>: <comment>
