---
id: EKS_REQUEST_FLOW
title: 'How It Works: EKS Request Flow'
type: documentation
relates_to:
  - ADR-0032-platform-eks-access-model
  - ADR-0144-intent-to-projection-parser
  - ADR-0161-ephemeral-infrastructure-stack
  - ADR-0168-eks-request-parser-and-mode-aware-workflows
  - CL-0142-eks-apply-scope-gate
  - CL-0143-eks-request-system
  - SCRIPT-0043
  - session-2026-01-17-eks-backstage-scaffolder
---

## How It Works: EKS Request Flow

This document explains how EKS cluster requests move from Backstage to a
governed request file, through validation and apply workflows, and finally into
Terraform state.

## 0. High-Level Architecture

```text
[Backstage EKS Template]
        |
        v
[PR with EKS request YAML]
        |
        v
[CI validation: parser + enums]
        |
        v
[Manual Apply Workflow]
        |
        v
[Terraform Apply]
        |
        v
[EKS Cluster + Bootstrap (if selected)]
```

## 1. Request Capture (Backstage)

The Backstage template collects the minimal set of inputs:

- `request_id` (EKS-0001)
- `environment`, `region`
- `mode` (cluster-only | bootstrap-only | cluster+bootstrap)
- `build_id` (required if mode includes cluster creation)
- `cluster_name`, `kubernetes_version`
- `node_tier`, `node_desired`, `node_max`, `capacity_type`

Result: a PR that adds a request file to:

```
docs/20-contracts/eks-requests/<env>/EKS-XXXX.yaml
```

## 2. Request Structure (Contract)

Requests are expressed in a nested spec so the parser can map them cleanly:

```yaml
id: EKS-0001
environment: dev
region: eu-west-2
owner: platform-team
requester: platform-team
spec:
  mode: cluster+bootstrap
  build:
    build_id: 17-01-26-01
  cluster:
    name: goldenpath-dev-eks-17-01-26-01
    kubernetes_version: "1.29"
  node_pool:
    node_tier: small
    desired: 3
    max: 5
    capacity_type: ON_DEMAND
```

## 3. Validation (CI)

PRs touching EKS request files run:

```
.github/workflows/ci-eks-request-validation.yml
```

This workflow validates:

- Required fields for the selected mode
- Enum alignment (`schemas/metadata/enums.yaml`)
- Node sizing rules (min <= desired <= max)
- Platform approval label is required for any EKS request PR

## 4. Parser (Intent to Projection)

The parser converts request files into deterministic tfvars:

```
scripts/eks_request_parser.py
```

Outputs:

```
envs/<env>/clusters/generated/<EKS-ID>.auto.tfvars.json
```

These outputs are the Terraform inputs used by the apply workflow.

## 5. Apply (Manual Workflow)

EKS applies are intentionally manual to avoid accidental rebuilds:

```
.github/workflows/eks-request-apply.yml
```

Key guardrails:

- Non-dev requires `allow_non_dev=true`
- `build_id` is used to select ephemeral state keys
- `bootstrap-only` skips Terraform apply and is handled separately

### Bootstrap-Only Workflow

Bootstrap-only requests use a dedicated workflow:

```
.github/workflows/eks-bootstrap-only.yml
```

It runs **after PR approval/merge** and only executes when the request mode is
`bootstrap-only`. Platform approval is required for all EKS requests; non-dev
workflow_dispatch runs also require `allow_non_dev=true`.

## 6. RDS Expectations (Ephemeral vs Persistent)

- **Ephemeral EKS**: coupled RDS is blocked by guardrails. Use standalone RDS
  requests if a team needs a database.
- **Persistent EKS**: coupled RDS is allowed and managed with the root state key.
- **Standalone RDS**: always available via the RDS request flow and lives in the
  platform RDS/VPC context (`envs/<env>-rds/`).

## 7. Notes and Known Gaps

- Size/tier approval guardrail is pending for large/xlarge tiers.
- `bootstrap-only` does not yet have a dedicated automation workflow.

---

## Related Files

- `docs/20-contracts/eks-requests/`
- `schemas/requests/eks.schema.yaml`
- `schemas/metadata/enums.yaml`
- `scripts/eks_request_parser.py`
- `.github/workflows/ci-eks-request-validation.yml`
- `.github/workflows/eks-request-apply.yml`
