# ADR-0020: Hybrid GitOps approach with Helm and Kustomize

- **Status:** Proposed
- **Date:** 2025-12-27
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Platform
- **Decision type:** Architecture | Operations
- **Related:** docs/09_ARCHITECTURE.md, docs/20_CI_ENVIRONMENT_SEPARATION.md
---

## Context

The repo already includes Helm-based GitOps and Kustomize overlays. We want a consistent, scalable
approach that keeps packaging benefits for third-party tools while making environment-specific
changes easy to audit.

---

## Decision

> We will adopt a hybrid GitOps approach: Helm for packaged apps and Kustomize for environment overlays.

Specifically:

- Use Helm for third-party platform apps and core packages.
- Use Kustomize overlays to apply environment-specific patches and app-of-apps structure.

---

## Scope

Applies to GitOps application definitions and environment customization in this repository.

---

## Consequences

### Positive

- Clear environment diffs with minimal patch sets.
- Leverages Helm packaging and dependency management.
- Reduces duplication and keeps env overrides explicit.

### Tradeoffs / Risks

- Two toolchains to maintain and document.
- Overlays can become verbose if patching is excessive.

### Operational impact

- Platform team maintains Helm values and Kustomize overlays.
- Documentation must stay aligned to avoid drift.

---

## Alternatives considered

- Helm-only approach (rejected: values files can become hard to audit per environment).
- Kustomize-only approach (rejected: weaker packaging for third-party apps).

---

## Follow-ups

- Document where Helm is required vs where overlays are used.
- Keep env overlays minimal and reviewed.

---

## Notes

This decision keeps the GitOps surface simple while preserving flexibility for growth.
