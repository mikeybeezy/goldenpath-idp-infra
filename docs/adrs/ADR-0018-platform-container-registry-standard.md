<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: ADR-0018-platform-container-registry-standard
title: 'ADR-0018: Container registry standard — ECR default, GHCR supported, Docker
  Hub discouraged'
type: adr
status: active
domain: platform-core
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 2
schema_version: 1
relates_to:
  - 01_adr_index
  - 22_CONTAINER_REGISTRY_STANDARD
  - ADR-0007-platform-environment-model
  - ADR-0008-app-backstage-portal
  - ADR-0018-platform-container-registry-standard
  - audit-20260103
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2027-01-03
version: '1.0'
breaking_change: false
---

# ADR-0018: Container registry standard — ECR default, GHCR supported, Docker Hub discouraged

- **Status:** Proposed
- **Date:** 2025-12-27
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Platform
- **Decision type:** Architecture | Security | Delivery
- **Related:** docs/adrs/ADR-0007-platform-environment-model.md, docs/adrs/ADR-0008-app-backstage-portal.md, docs/10-governance/01_GOVERNANCE.md

---

## Context

GoldenPath V1 targets an AWS-first, EKS-based platform with:

- private-by-default networking
- frequent cluster teardown and rebuild
- CI-driven image build and promotion
- deterministic outcomes and low operational friction

Container registry choice affects:

- network egress cost and reliability (NAT dependency)
- authentication and access control complexity
- image pull performance during bootstrap
- security scanning and audit posture

We want a default that aligns with these constraints while keeping team flexibility.

---

## Decision

> We will use Amazon ECR as the default registry for platform and reference workloads.

Additionally:

- GHCR is supported as an alternative when GitHub-native workflows are preferred.
- Docker Hub is permitted for public base images but discouraged as the primary registry for platform workloads.

This is an opinionated default, not a hard block.

---

## Scope

- Applies to platform-owned images (e.g., Backstage), reference pipelines, and default templates.
- Does not mandate registry choice for all teams or external integrations.
- Does not prohibit pulling public images from Docker Hub.

---

## Consequences

### Positive

- Fewer network and auth surprises during cluster bootstrap.
- Clear default for teams adopting the platform.
- Improved determinism for rebuild scenarios.
- Aligns with AWS-first posture and IAM-based auth.

### Tradeoffs / Risks

- Increased coupling to AWS in V1.
- Non-AWS teams may prefer GHCR or another registry.
- Migration required if the default changes later.

### Mitigations

- Registry URLs remain configurable per environment.
- Templates avoid hardcoded registry assumptions where possible.
- Alternative registries are supported with documented patterns.

---

## Alternatives considered

- GHCR as default (rejected: NAT/egress dependency for private EKS clusters).
- Docker Hub as default (rejected: rate limits, external dependency, weaker governance fit).
- Registry-agnostic default (rejected for V1: increases decision burden).

---

## Follow-ups

- Update platform documentation to reflect registry defaults and alternatives.
- Provide reference CI pipelines for:
  - ECR (default)
  - GHCR (supported alternative)
- Define scanning guidance independent of registry choice (CI scan + registry scan).

---

## Notes

Even with ECR, keep references registry-agnostic and configurable per environment.
