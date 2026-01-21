---
id: session-capture-2026-01-21-tooling-resolution
title: Tooling Resolution - Dev Environment Fixes and Matrix Restructure
type: documentation
domain: platform-core
owner: platform-team
lifecycle: active
status: active
schema_version: 1
risk_profile:
  production_impact: medium
  security_risk: low
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
  maturity: 2
relates_to:
  - 20_TOOLING_APPS_MATRIX
  - 30_DEV_BASELINE_CHECKLIST
  - APPS_DEV_EXTERNAL_SECRETS
  - APPS_DEV_CLUSTER_SECRET_STORE
  - APPS_DEV_KONG
  - APPS_DEV_KEYCLOAK
  - APPS_DEV_BACKSTAGE
---

# Session Capture: Tooling Resolution

## Session metadata

**Agent:** Claude Opus 4.5
**Date:** 2026-01-21
**Timestamp:** 2026-01-21T10:00:00Z
**Branch:** tooling/resolution

## Scope

- Fix dev environment tooling issues (Kong, Backstage, Keycloak, Grafana datasources)
- Ensure components work out-of-the-box after bootstrap
- Restructure tooling matrix to include internal/infrastructure components
- Update dev baseline checklist with verification steps

## Problem Statement

User reported the following issues in the dev environment:
1. Kong - no data coming through
2. Backstage - not showing
3. Keycloak - not working
4. Grafana datasources - not picking up any data

Root cause analysis identified:
- Missing ClusterSecretStore ArgoCD application (ExternalSecrets couldn't sync)
- No sync-wave ordering for dependencies (apps deploying before prerequisites ready)
- Missing Tempo datasource in Grafana configuration

## Work Summary

### Phase 1: Dependency and Sync-Wave Fixes

- Added sync-wave annotations to enforce deployment order:
  - external-secrets: wave 0 (foundation)
  - cluster-secret-store: wave 1 (requires ESO CRDs)
  - kong: wave 2 (ingress gateway)
  - keycloak: wave 3 (identity provider)
  - kube-prometheus-stack: wave 4 (observability)
  - backstage: wave 5 (developer portal)

- Created new ClusterSecretStore ArgoCD application to deploy the AWS Secrets Manager store

- Added Tempo datasource to Grafana with trace-to-logs correlation

### Phase 2: Tooling Matrix Restructure

User observation: Matrix only had user-facing components, missing internal components like cert-manager, coredns, external-dns that have version numbers.

Implemented 4-tier categorization:
- **Tier 1**: EKS Managed Add-ons (coredns, kube-proxy, vpc-cni, CSI drivers)
- **Tier 2**: Platform Infrastructure (cluster-autoscaler, aws-load-balancer-controller, metrics-server)
- **Tier 3**: Platform Services (external-secrets, kong, keycloak, observability stack)
- **Tier 4**: Developer-Facing Apps (backstage, hello-goldenpath-idp)

## Artifacts Touched (links)

### Added

- `gitops/argocd/apps/dev/cluster-secret-store.yaml` - New ArgoCD app for ClusterSecretStore deployment

### Modified

- `gitops/argocd/apps/dev/external-secrets.yaml` - Added sync-wave 0, labels, owner annotation
- `gitops/argocd/apps/dev/kong.yaml` - Added sync-wave 2
- `gitops/argocd/apps/dev/keycloak.yaml` - Added sync-wave 3
- `gitops/argocd/apps/dev/backstage.yaml` - Added sync-wave 5
- `gitops/helm/kube-prometheus-stack/values/dev.yaml` - Added Tempo datasource with trace-to-logs
- `bootstrap/50_smoke-tests/30_dev_baseline_checklist.md` - Added verification sections for External Secrets, Identity, Developer Portal, Observability
- `docs/70-operations/20_TOOLING_APPS_MATRIX.md` - Complete restructure into 4-tier categories

### Referenced / Executed

- `modules/aws_eks/main.tf` - EKS add-on definitions (lines 188-306)
- `envs/dev/terraform.tfvars` - Cluster and add-on configuration
- `gitops/kustomize/bases/external-secrets/` - ClusterSecretStore base manifests

## Validation

- `git status` - Verified changes staged correctly
- `git push origin tooling/resolution` - Successfully pushed to remote

## Key Decisions

1. **Sync-wave over manual ordering**: Using ArgoCD sync-waves ensures deterministic deployment order without manual intervention

2. **Separate ClusterSecretStore app**: Rather than bundling with external-secrets helm chart, using separate Kustomize app allows:
   - Independent lifecycle management
   - Clear wave separation (ESO must be ready before ClusterSecretStore)
   - Easier debugging of secret store issues

3. **4-tier matrix structure**: Balances comprehensiveness with clarity:
   - EKS add-ons managed by AWS (Terraform)
   - Infrastructure managed by bootstrap/Helm
   - Services managed by ArgoCD with sync-waves
   - Apps managed by ArgoCD

## Current State / Follow-ups

### Completed
- Sync-wave annotations added to all critical apps
- ClusterSecretStore ArgoCD app created
- Tempo datasource added to Grafana
- Tooling matrix restructured with all versioned components
- Dev baseline checklist updated

### Requires Verification (Post-Deploy)
- [ ] Verify ClusterSecretStore becomes `Ready` after ESO syncs
- [ ] Verify ExternalSecrets for Keycloak and Backstage sync successfully
- [ ] Verify Kong LoadBalancer gets EXTERNAL-IP
- [ ] Verify Grafana can query Prometheus, Loki, and Tempo
- [ ] Verify Backstage UI loads at https://backstage.dev.goldenpathidp.io

### Future Enhancements
- Consider adding health checks to sync-waves (ArgoCD resource hooks)
- Add Argo CD notifications for sync failures
- Create automated smoke test script based on baseline checklist

Signed: Claude Opus 4.5 (2026-01-21T12:00:00Z)

---

## Updates (append as you go)

### Update - 2026-01-21T11:30:00Z

**What changed**
- Created tooling/resolution branch from development
- Added sync-wave annotations to external-secrets, kong, keycloak, backstage
- Created cluster-secret-store.yaml ArgoCD application
- Added Tempo datasource to kube-prometheus-stack values

**Artifacts touched**
- `gitops/argocd/apps/dev/external-secrets.yaml`
- `gitops/argocd/apps/dev/kong.yaml`
- `gitops/argocd/apps/dev/keycloak.yaml`
- `gitops/argocd/apps/dev/backstage.yaml`
- `gitops/argocd/apps/dev/cluster-secret-store.yaml` (new)
- `gitops/helm/kube-prometheus-stack/values/dev.yaml`
- `bootstrap/50_smoke-tests/30_dev_baseline_checklist.md`

**Validation**
- `git commit` - Committed with message "fix: add sync-wave ordering and cluster-secret-store for dev environment"
- `git push origin tooling/resolution` - Pushed successfully

**Next steps**
- Restructure tooling matrix per user feedback

**Outstanding**
- Tooling matrix restructure pending

Signed: Claude Opus 4.5 (2026-01-21T11:30:00Z)

---

### Update - 2026-01-21T12:00:00Z

**What changed**
- Restructured tooling matrix into 4-tier component categories
- Added Tier 1: EKS Managed Add-ons (coredns, kube-proxy, vpc-cni, aws-ebs-csi-driver, aws-efs-csi-driver, snapshot-controller)
- Added Tier 2: Platform Infrastructure (cluster-autoscaler, aws-load-balancer-controller, metrics-server)
- Added sync-wave column to all quick reference tables
- Added detailed documentation sections for all new components
- Updated changelog

**Artifacts touched**
- `docs/70-operations/20_TOOLING_APPS_MATRIX.md` (+285 lines)

**Validation**
- `git commit` - Committed with message "docs: restructure tooling matrix into tiered component categories"
- `git push origin tooling/resolution` - Pushed successfully (3769c3df)

**Next steps**
- Merge tooling/resolution to development when ready
- Deploy to dev cluster and verify fixes

**Outstanding**
- None - all planned work complete

Signed: Claude Opus 4.5 (2026-01-21T12:00:00Z)

---

## Sync-Wave Deployment Order Reference

```text
Wave -1: Infrastructure Controllers
  └── cluster-autoscaler
  └── aws-load-balancer-controller

Wave 0: Foundation
  └── external-secrets (ESO operator)
  └── external-dns
  └── cert-manager

Wave 1: Secret Stores
  └── cluster-secret-store (ClusterSecretStore CR)

Wave 2: Ingress Gateway
  └── kong

Wave 3: Identity Provider
  └── keycloak

Wave 4: Observability Stack
  └── kube-prometheus-stack
  └── loki
  └── tempo
  └── fluent-bit

Wave 5: Developer Portal
  └── backstage

Wave 6: Sample Applications
  └── hello-goldenpath-idp
```

---

## Commits Summary

| Commit | Message | Files Changed |
|--------|---------|---------------|
| 70615407 | fix: add sync-wave ordering and cluster-secret-store for dev environment | 7 |
| 3769c3df | docs: restructure tooling matrix into tiered component categories | 1 |

---

### Update - 2026-01-21T14:30:00Z

**What changed**
- Fixed prometheus-operator ImagePullBackOff (double registry prefix `quay.io/quay.io/...`)
- Separated registry and repository fields in kube-prometheus-stack values
- Applied fix to both dev.yaml and local.yaml
- Created Grafana dashboard ConfigMap for hello-goldenpath-idp following tooling dashboard pattern

**Root Cause**
- kube-prometheus-stack chart expects separate `registry` and `repository` fields
- When full path provided in `repository`, chart prepended default registry
- Result: `quay.io/quay.io/prometheus-operator/prometheus-operator:v0.68.0`
- Without prometheus-operator, no Prometheus/Alertmanager StatefulSets created

**Artifacts touched**
- `gitops/helm/kube-prometheus-stack/values/dev.yaml` - Fixed image configuration for all components
- `gitops/helm/kube-prometheus-stack/values/local.yaml` - Applied same fix
- `hello-goldenpath-idp/deploy/base/dashboards/hello-goldenpath-idp-dashboard.yaml` (new)
- `hello-goldenpath-idp/deploy/base/kustomization.yaml` - Added dashboard resource

**Validation**
- Verified image paths no longer have double registry prefix
- Dashboard ConfigMap follows tooling dashboard pattern with grafana_dashboard label

**Next steps**
- Push hello-goldenpath-idp changes
- Verify Grafana sidecar picks up dashboard after ArgoCD sync
- Verify Prometheus metrics flow to Grafana dashboards

**Outstanding**
- Verify fixes after ArgoCD sync

Signed: Claude Opus 4.5 (2026-01-21T14:30:00Z)

---

## Review/Validation Appendix

*To be completed after deployment verification*
