# Source of Truth (Stub)

## Intent
Clarify which system is authoritative for infrastructure, platform config, and
runtime state so drift can be detected and reconciled consistently.

## Current stance (summary)
- Git repos define desired state for platform apps and manifests.
- Terraform state is authoritative for cloud infrastructure.
- Runtime clusters are observed state, not the source of truth.

## Notes
- This file is a stub to anchor ADR references until expanded.
- Related: `docs/40-delivery/12_GITOPS_AND_CICD.md`.
