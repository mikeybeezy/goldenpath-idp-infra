# ADR-0023: CI image scanning standard

- **Status:** Proposed
- **Date:** 2025-12-27
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Platform
- **Decision type:** Security | Delivery
- **Related:** docs/01_GOVERNANCE.md, docs/22_CONTAINER_REGISTRY_STANDARD.md
---

## Context

We need a registry-agnostic image vulnerability gate in CI. The platform should provide a default
scanner that works with ECR, GHCR, or other registries, while keeping future options open.

---

## Decision

> We will use Trivy as the default CI image scanner, with an opinionated gate policy.

Policy:

- Fail builds on HIGH/CRITICAL vulnerabilities for production pipelines.
- Warn (do not fail) on HIGH/CRITICAL for dev/test unless explicitly tightened.
- Allow teams to add additional scanners (ECR enhanced scanning, Docker Scout) as optional layers.

---

## Scope

Applies to CI pipelines that build or scan container images in this repository.

---

## Consequences

### Positive

- Consistent, registry-agnostic security gate.
- Fast feedback early in the pipeline.
- Compatible with AWS-first and GitHub-native workflows.

### Tradeoffs / Risks

- Trivy results can vary based on database freshness.
- False positives can cause churn if thresholds are too strict.

### Operational impact

- Maintain Trivy versions in CI.
- Keep gate policy consistent across pipelines.

---

## Alternatives considered

- Docker Scout as default (rejected: licensing and Docker org dependency).
- ECR enhanced scanning only (rejected: ECR-specific, not registry-agnostic).

---

## Follow-ups

- Add a CI job or reusable workflow for Trivy scanning.
- Optionally publish SARIF results to GitHub Security.

---

## Notes

This sets the baseline; teams may extend with additional scanners.
