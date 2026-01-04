---
id: 10_INFRA_FAILURE_MODES
title: Infra Failure Modes and Recovery
type: documentation
category: unknown
version: '1.0'
owner: platform-team
status: active
dependencies: []
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to:
  - 15_TEARDOWN_AND_CLEANUP
---

# Infra Failure Modes and Recovery

This document captures common infrastructure build failures, how we recover,
and the options we considered.

## Common failure modes

- IAM role collisions (`EntityAlreadyExists`) from previous builds.
- EKS node groups failing to join (no NAT for private subnets).
- Orphaned load balancers/ENIs preventing VPC teardown.
- Terraform state drift (resources created outside the current state).

## Chosen approach (V1)

1) Use a build ID and lifecycle tagging strategy to prevent collisions.
2) Use a cleanup script to delete orphaned resources by `BuildId`.

This combination avoids name collisions, makes cleanup deterministic, and
reduces manual imports.

## Operational flow when a build fails

1) Stop the failed apply.
2) Run the cleanup script for that `BuildId` (dry-run first).
3) Re-run `terraform apply` once cleanup is complete.
4) Import resources only if you intend to keep them.

## Automation note

We do not auto-run cleanup on failure because it can break Terraform
idempotency. If you want automation, wire `bootstrap/60_tear_down_clean_up/cleanup-orphans.sh` behind an
explicit flag in CI (e.g., only when you intend to abandon a build).

Cleanup script:

```text

bootstrap/60_tear_down_clean_up/cleanup-orphans.sh <build-id> <region>

```text

Set `DRY_RUN=false` to execute deletions. For manual AWS cleanup, see
`docs/70-operations/15_TEARDOWN_AND_CLEANUP.md`.

Build ID decision:

```text

docs/40-delivery/16_INFRA_Build_ID_Strategy_Decision.md

```text

## Terraform Kubernetes resources (decision)

**Problem:** Terraform fails when Kubernetes API access is unavailable
(`connect: connection refused`) while trying to manage service accounts.

## Options considered:

1) **Single Terraform apply** that includes Kubernetes resources.

   - Pros: one command.
   - Cons: brittle when kubeconfig or cluster readiness is missing.

2) **Split into phases**: AWS/EKS first, then Kubernetes resources.

   - Pros: reliable and CI-friendly; avoids kube-provider failures.
   - Cons: requires a second apply (unless automated).

3) **Conditional Kubernetes resources** behind a flag.

   - Pros: avoids failure until kube access exists.
   - Cons: needs a second apply to enable later.

**Decision (V1):** Use **phase 2 via the bootstrap runner**. The runner
applies `enable_k8s_resources=true` after kubeconfig is set, so users still
run a single command while CI remains reliable. Trade-off is an extra apply
under the hood, which is acceptable for stability.

## Other options we can adopt later

- Separate AWS accounts per environment (best isolation, higher overhead).
- Workspace-per-build for state isolation (does not prevent name collisions).
- Random suffixes for all names (prevents collisions, harder to read).
- Scheduled sweeper job to purge expired BuildIds.

## GitOps OutOfSync noise (to revisit)

Some apps (e.g., Kong) generate runtime certificates and webhook `caBundle`
values. Argo CD will report these as OutOfSync even when the app is healthy.
This creates alert fatigue and can hide real drift. We should add explicit
`ignoreDifferences` rules for these known dynamic fields and keep the list
under review.
