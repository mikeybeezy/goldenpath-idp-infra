---
id: 12_GITOPS_AND_CICD
title: GitOps and CI/CD
type: documentation
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - 01_GOVERNANCE
  - 04_REPO_STRUCTURE
  - 06_IDENTITY_AND_ACCESS
  - 08_SOURCE_OF_TRUTH
  - 16_INFRA_Build_ID_Strategy_Decision
  - 17_BUILD_RUN_FLAGS
  - ADR-0001-platform-argocd-as-gitops-operator
  - BOOTSTRAP_10_BOOTSTRAP_README
  - RELATIONSHIP_EXTRACTION_GUIDE
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---
# GitOps and CI/CD

Doc contract:

- Purpose: Explain GitOps and CI/CD flow and Argo CD usage.
- Owner: platform
- Status: reference
- Review cadence: as needed
- Related: docs/20-contracts/29_CD_DEPLOYMENT_CONTRACT.md, docs/40-delivery/26_POST_APPLY_HEALTH_CHECKS.md, docs/adrs/ADR-0001-platform-argocd-as-gitops-operator.md

This document explains how the platform delivers changes using GitOps and
CI/CD. It keeps Argo CD details in one place.

## Goals

- Single source of truth in Git.
- Clear ownership of platform vs application delivery.
- Predictable promotion across environments.

## Current model (V1)

- **GitOps engine**: Argo CD.
- **CI**: GitHub Actions (pipeline details evolve by repo).
- **Source of truth**: this repo for platform tooling and shared services.

## Repository layout

- `gitops/argocd/apps/<env>`: Argo CD Application manifests per environment.
- `gitops/helm/<app>/values/<env>.yaml`: Helm values overrides per environment.

## Bootstrap flow (high level)

1) Terraform provisions infra and EKS add-ons.
2) Bootstrap runner installs Argo CD.
3) Argo CD Applications are applied from `gitops/argocd/apps/<env>`.
4) Argo CD reconciles apps to match Git.

## Sync policy

- Default is manual sync during bootstrap and early iterations.
- Auto-sync can be enabled later when drift and promotion rules are stable.

## Access and RBAC (bootstrap phase)

- Admin access is allowed temporarily for bootstrap.
- Use port-forward for Argo CD if there is no external Service.
- Tighten RBAC after bootstrap and route access through SSO.

Service account access and IRSA bindings are governed in:

`docs/60-security/06_IDENTITY_AND_ACCESS.md`

## Drift handling

Some apps generate runtime state (e.g., webhook certificates). These should be
ignored via `ignoreDifferences` rules to prevent persistent OutOfSync noise.

## ignoreDifferences (noise reduction)

We apply `ignoreDifferences` only to controller‑managed fields so Argo “OutOfSync”
remains meaningful. Current scope:

- **Kong**: webhook CA bundles and webhook‑managed secrets.
- **cert‑manager**: webhook CA bundles.

Rules live in the per‑env Argo Application manifests under
`gitops/argocd/apps/<env>/`.

## Custom health checks for CRDs

We define custom health checks for noisy CRDs so “Unknown” becomes actionable.
These checks are configured in Argo CD values under:

`gitops/helm/argocd/values/<env>.yaml`

Current coverage:

- **cert‑manager**: `Certificate`, `ClusterIssuer`
- **Kong**: `KongPlugin`, `KongIngress`, `KongConsumer`, `KongClusterPlugin`

## CI/CD integration (future)

- Pipeline creates or updates Argo CD Application manifests.
- Sync gates include preflight checks and environment approvals.
- Promotion is a Git change, not a manual kubectl step.

## CI runner CLI requirements

These tools are referenced by the Makefile and bootstrap/teardown scripts in
this repo, so CI/CD agents should have them installed:

- `aws` (AWS CLI)
- `terraform`
- `kubectl`
- `helm`
- `awk`
- `sed`
- `bash`

Notes:

- `rg` (ripgrep) appears only in notes (`chat_fil.txt`), not required for CI.
- No `jq`/`json` CLI usage found in repo scripts.
- Standard shell utilities like `grep`, `tr`, `sort`, `head`, and `date` are

  used by scripts and are expected to be available in the runner image.

### Version guidance (observed)

The bootstrap README includes an example run with these tool versions. Use
these as a starting point if you want to pin CI images:

- AWS CLI: 1.33.35
- kubectl: v1.32.3
- Helm: v3.10.3

Source: `bootstrap/10_bootstrap/README.md`.

## CI build metadata (ephemeral runs)

For ephemeral runs, CI should pass build metadata into Terraform so tags and
names are deterministic. This keeps cleanup predictable and avoids IAM role
collisions. See `docs/40-delivery/16_INFRA_Build_ID_Strategy_Decision.md`.

For the full list of build/bootstrap/teardown flags used in CI, see
`docs/40-delivery/17_BUILD_RUN_FLAGS.md`.

Example:

```bash

export TF_VAR_cluster_lifecycle=ephemeral
export TF_VAR_build_id=$GITHUB_RUN_NUMBER
export TF_VAR_owner_team=platform-team

```text

Bootstrap runner note:

- If `TF_DIR` is set, the runner reads `cluster_name` and `region` from

  `TF_DIR/terraform.tfvars` when positional args are omitted.

- If `SCALE_DOWN_AFTER_BOOTSTRAP=true`, set `TF_AUTO_APPROVE=true` to avoid

  interactive approval during the scale-down apply.

- Recommended default is `SCALE_DOWN_AFTER_BOOTSTRAP=false` until Argo apps

  and add-ons converge; scale down after verifying health and capacity.

## Reference build timing

A clean dev build (Terraform apply + bootstrap) has recently completed in
~15 minutes. Treat this as a baseline and update as we gather more CI data.

## CI bootstrap workflow (stub)

We keep a staged GitHub Actions workflow that mirrors the bootstrap flow and
teardown guardrails. It is intentionally stubbed so each phase can be wired in
incrementally without changing the order.

`/.github/workflows/ci-bootstrap.yml`

## CI Backstage workflow (stub)

We keep a minimal Backstage CI workflow stub that mirrors the first‑app flow
and can be wired in phase by phase.

`/.github/workflows/ci-backstage.yml`

Phases:

1) Preflight checks
2) Terraform init/plan/apply
3) Bootstrap runner
4) Post-bootstrap validation
5) Optional teardown (ephemeral only)

Trigger it manually from GitHub Actions using workflow dispatch inputs.
