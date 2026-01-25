<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: RB-0012-argocd-app-readiness
title: Argo CD App Readiness Checklist
type: runbook
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: medium
  security_risk: access
  coupling_risk: medium
reliability:
  rollback_strategy: rerun-validation
  observability_tier: silver
  maturity: 1
schema_version: 1
relates_to:
  - 00_DOC_INDEX
  - 05_GOLDEN_PATH_VALIDATION
  - 10_INFRA_FAILURE_MODES
  - 29_CD_DEPLOYMENT_CONTRACT
  - ADR-0001-platform-argocd-as-gitops-operator
  - ADR-0013-platform-argo-app-management-approach
  - ADR-0158-platform-standalone-rds-bounded-context
  - BOOTSTRAP_README
  - DOCS_RUNBOOKS_README
  - RB-0013-leak-protection-management
  - RB-0031-idp-stack-deployment
supersedes: []
superseded_by: []
tags: []
inheritance: {}
status: active
supported_until: 2028-01-01
version: 1.0
dependencies:
  - chart:argo-cd
breaking_change: false
---

# Argo CD App Readiness Checklist

Doc contract:

- Purpose: Verify Argo CD apps can sync cleanly and required dependencies exist.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/70-operations/runbooks/05_GOLDEN_PATH_VALIDATION.md, docs/20-contracts/29_CD_DEPLOYMENT_CONTRACT.md, docs/70-operations/10_INFRA_FAILURE_MODES.md

Last updated: 2026-01-03

Use this checklist after infra apply and before/after bootstrap to confirm
Argo CD apps are ready to sync without manual fixes.

## Inputs

- ENV: `dev|test|staging|prod`
- App manifests: `gitops/argocd/apps/${ENV}`

## 1) Static validation (repo)

Confirm value files and paths exist:

```bash
rg -n -F '$values/' "gitops/argocd/apps/${ENV}" -g '*.yaml'
rg -n 'path:' "gitops/argocd/apps/${ENV}" -g '*.yaml'
```

Verify each referenced file/path exists in the repo.

## 2) Namespaces

Each app manifest should include `CreateNamespace=true`. Verify for the env:

```bash
rg -n 'CreateNamespace=true' "gitops/argocd/apps/${ENV}" -g '*.yaml'
```

## 3) External dependencies

Confirm these exist before expecting app sync to succeed:

- **OIDC + IAM roles (IRSA):** required for controllers (e.g., cluster-autoscaler).
- **Secrets:** any app requiring credentials must have secrets present.
- **CRDs:** cert-manager, external-secrets, datree, kong, etc. must register CRDs.

Suggested checks (cluster required):

```bash
kubectl get crds | rg 'cert-manager|external-secrets|kong|datree'
kubectl get sa -n kube-system | rg 'cluster-autoscaler'
```

## 4) Argo CD status

Validate app health and sync status:

```bash
argocd app list
argocd app get <app-name>
```

Expected: `Healthy` and `Synced` or a clear, actionable diff.

## 5) Kubernetes runtime checks

Confirm app workloads are running:

```bash
kubectl get ns
kubectl get pods -n <namespace>
kubectl get svc -n <namespace>
```

## Failure handling

- If CRDs are missing, sync the CRD-providing chart first.
- If IRSA errors appear, verify OIDC provider + IAM role bindings.
- If secrets are missing, create or sync the secret source before re-sync.
