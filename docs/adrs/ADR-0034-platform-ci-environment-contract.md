---
id: ADR-0034-platform-ci-environment-contract
title: 'ADR-0034: CI Environment Contract'
type: adr
status: active
domain: platform-core
lifecycle: active
version: '1.0'
relates_to:
  - ADR-0011
  - ADR-0011-platform-ci-environment-contract
  - ADR-0034
supported_until: 2027-01-03
breaking_change: false
---

# ADR-0034: CI Environment Contract

- **Status:** Accepted
- **Date:** 2025-12-27
- **Owners:** Platform (GoldenPath IDP)
- **Decision type:** Governance / Delivery
- **Related docs:** docs/10-governance/01_GOVERNANCE.md, docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md
- **Legacy alias:** docs/adrs/ADR-0011-platform-ci-environment-contract.md

## Context

GoldenPath relies on CI pipelines to provision infrastructure, bootstrap clusters, deploy platform tooling, and tear environments down deterministically.
As the system evolved, pipeline behavior became increasingly influenced by environment variables that control:

- target environment selection
- cluster naming and lifecycle
- conditional execution paths (apply vs destroy)
- promotion and bootstrap behavior

Without an explicit contract, these variables risk becoming:

- implicit knowledge held by individuals
- undocumented coupling between workflows and scripts
- a source of non-deterministic or surprising behavior

This creates operational risk and makes delegation, refactoring, and onboarding harder over time.

## Decision

GoldenPath defines an explicit **CI Environment Contract**.

All environment variables that influence CI pipeline behavior are treated as a **governed interface** between:

- CI workflows
- infrastructure provisioning
- bootstrap scripts
- GitOps reconciliation

These variables must be:

- explicitly named
- documented
- intentional

Any change that alters CI behavior through environment variables requires:

- an update to the CI Environment Contract document
- an Architecture Decision Record if the change affects platform semantics

## Consequences

### Positive

- CI behavior becomes predictable and repeatable.
- Pipelines fail fast when required inputs are missing.
- Knowledge moves from individual memory into durable artifacts.
- Refactoring pipelines becomes safer and more intentional.
- The platform becomes easier to operate without the original author present.

### Tradeoffs

- Slight upfront discipline when introducing or changing variables.
- Additional documentation to maintain as the system evolves.

These tradeoffs are accepted to reduce long-term operational risk and cognitive load.

## Alternatives Considered

- **Implicit environment variables:** Rejected due to hidden coupling and poor debuggability.
- **Inline documentation in workflows only:** Rejected due to duplication and lack of a single source of truth.
- **Relying solely on GitHub-provided variables:** Rejected as insufficient for platform-specific behavior.

## Notes

The CI Environment Contract is expected to evolve as the platform matures.
This ADR records the decision to formalize the contract, not the contents of the contract itself.
This ADR supersedes `docs/adrs/ADR-0011-platform-ci-environment-contract.md`.
