---
id: ADR-0040
title: ADR-0040: Lifecycle-aware Terraform state keys for BuildId isolation
type: adr
owner: platform-team
status: active
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: 2027-01-03
  breaking_change: false
relates_to: []
---

# ADR-0040: Lifecycle-aware Terraform state keys for BuildId isolation

Filename: `ADR-0040-platform-lifecycle-aware-state-keys.md`

- **Status:** Proposed
- **Date:** 2025-12-29
- **Owners:** `platform`
- **Domain:** Platform
- **Decision type:** Operations
- **Related:** `docs/70-operations/36_STATE_KEY_STRATEGY.md`, `docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md`, `docs/70-operations/32_TERRAFORM_STATE_AND_LOCKING.md`, `.github/workflows/infra-terraform.yml`, `.github/workflows/infra-terraform-apply-dev.yml`, `.github/workflows/ci-bootstrap.yml`, `.github/workflows/ci-teardown.yml`, `.github/workflows/pr-terraform-plan.yml`

---

## ADR immutability

ADRs are **immutable once created**. If a decision changes, write a new ADR and
mark the old one as **Superseded** with a reference to the new ADR.
Do not delete or rewrite prior ADRs.

---

## Context

Ephemeral builds were reusing the persistent Terraform state key. New BuildIds
would still load old state, leading to stale plans, drift reconciliation, and
accidental reuse of resources. We need a clean-slate experience for ephemeral
builds without losing the ability to update long-lived infrastructure.

Constraints:
- CI must enforce the correct state key without relying on operators to pass it.
- BuildId must be required for ephemeral runs.
- Persistent environments must keep a stable state key.

---

## Decision

We will resolve Terraform backend state keys based on lifecycle:

- **Persistent:** `envs/<env>/terraform.tfstate`
- **Ephemeral:** `envs/<env>/builds/<build_id>/terraform.tfstate`

CI workflows that init Terraform will use this rule (plan, apply, bootstrap,
teardown, and PR plan). Ephemeral runs will require `build_id`, and the plan/apply
gate will enforce that the plan and apply use the same lifecycle and BuildId.

When a new ephemeral build is explicitly requested, CI must fail if the
state key already exists. This avoids accidentally appending to an old build.

---

## Scope

Applies to:
- CI workflows in this repo for infra plan/apply/bootstrap/teardown.
- Dev environment state (S3 + DynamoDB).

Does not apply to:
- Local runs unless the operator passes the same backend key manually.
- Non-terraform tooling state (e.g., Argo, Helm).

---

## Consequences

### Positive

- New BuildId equals a new state key, guaranteeing a fresh slate for ephemeral runs.
- Persistent environments keep stable state for incremental changes.
- Plans and applies align on the same state key, reducing drift confusion.

### Tradeoffs / Risks

- More state objects in S3; requires lifecycle cleanup policy.
- Operators must be disciplined about BuildId reuse when updating an existing ephemeral build.
- Accidental new BuildId can create a new cluster and incur cost.

### Operational impact

- CI roles must allow access to the `envs/<env>/builds/*` prefix.
- Docs and runbooks must explain how to choose lifecycle and BuildId.
- Support teams must confirm lifecycle/build_id before diagnosing plan output.

---

## Alternatives considered

- **Single state key with tagging:** rejected due to drift and stale plan output.
- **Terraform workspaces:** rejected for higher cognitive overhead and operator error.
- **Separate buckets per build:** rejected for operational overhead and IAM complexity.

---

## Follow-ups

- Update IAM policies to allow `envs/<env>/builds/*` state access for apply/plan roles.
- Add lifecycle cleanup for old ephemeral state objects.
- Document the CI path for persistent updates vs ephemeral fresh builds.

---

## Notes

If this decision changes, create a new ADR and mark this one as superseded.
