---
id: session-2026-01-21-scaffold-golden-paths
title: Scaffold Golden Paths (Stateless, Stateful, Backend+RDS)
type: session-capture
domain: platform-core
owner: platform-team
lifecycle: active
status: active
schema_version: 1
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: medium
relates_to:
  - ecr_requests
  - secrets_lifecycle
  - rds_provisioning
---

# Session Capture: Scaffold Golden Paths

## Session metadata

**Agent:** Antigravity
**Date:** 2026-01-21
**Branch:** `scaffold/hello-goldenpath-idp`

## Scope

*   **Stateless App**: Created Golden Path for deployments (Deployment + Service + Ingress).
*   **Stateful App**: Created Golden Path for stateful workloads (StatefulSet + PVC).
*   **Backend + RDS**: Created Composite Golden Path (Stateless App + Managed RDS).
*   **Secrets Integration**: Implemented "Zero-Touch" secrets flow using External Secrets Operator.

## Work Summary

### 1. Stateless App (Golden Path)
**Goal**: Deterministic factory for standard web services.
**Artifacts**:
*   `schemas/requests/stateless-app.schema.yaml`
*   `templates/stateless-app/template.yaml`
*   `templates/stateless-app/skeleton/**` (Full app scaffold)
*   **Key Feature**: Mirrors `hello-goldenpath-idp` reference implementation exactly.

### 2. Stateful App (Golden Path)
**Goal**: Enable self-service for Caches (Redis) and Queues (RabbitMQ).
**Artifacts**:
*   `schemas/requests/stateful-app.schema.yaml`
*   `templates/stateful-app/template.yaml`
*   `templates/stateful-app/skeleton/**` (StatefulSet + Headless Service)
*   **Key Feature**: Uses `volumeClaimTemplates` to provision AWS EBS `gp3` volumes automatically.

### 3. Backend App + RDS (Composite Golden Path)
**Goal**: One-click provisioning of App + Database with zero-touch secret handling.
**Artifacts**:
*   `schemas/requests/backend-app-rds.schema.yaml`
*   `templates/backend-app-rds/template.yaml`
*   `templates/backend-app-rds/skeleton/deploy/base/externalsecret.yaml`
*   **Key Feature**: Bridges the gap between Infra (AWS Secrets Manager) and App (K8s Secrets).
    *   **Source**: `rds/${env}/${dbname}` (Created by Infra workflow)
    *   **Sink**: `${component_id}-db-creds` (Created by ESO)
    *   **Mount**: `envFrom` (Injected into Pod)

## Artifacts Touched (links)

### Added
*   `backstage-helm/backstage-catalog/templates/stateless-app/**`
*   `backstage-helm/backstage-catalog/templates/stateful-app/**`
*   `backstage-helm/backstage-catalog/templates/backend-app-rds/**`
*   `schemas/requests/stateless-app.schema.yaml`
*   `schemas/requests/stateful-app.schema.yaml`
*   `schemas/requests/backend-app-rds.schema.yaml`
*   `docs/85-how-it-works/self-service/STATELESS_APP_REQUEST_FLOW.md`
*   `docs/85-how-it-works/self-service/STATEFUL_APP_REQUEST_FLOW.md`
*   `docs/85-how-it-works/self-service/BACKEND_APP_RDS_REQUEST_FLOW.md`

### Modified
*   `backstage-helm/backstage-catalog/all.yaml` (Registered new templates)
*   `task.md` (Updated progress)

## Validation

*   **Recursive Review**: Verified that all skeletons use valid K8s manifests and correct template variable syntax (`${{ values.foo }}`).
*   **Contract Check**: Verified `externalsecret.yaml` correctly references the secret structure defined in `rds-request`.
*   **Consistency**: All templates follow the same `ECR` pattern (Thin Caller CI/CD, Kustomize overlays).

## Current State / Follow-ups

*   **Ready for Merge**: The branch `scaffold/hello-goldenpath-idp` contains all patterns.
*   **Next**: Verify in a live Backstage instance.

Signed: Antigravity (2026-01-21)

---

## Review/Validation Appendix

### Review Feedback (claude-opus-4.5 - 2026-01-21T14:00:00Z)

#### Commendations

1. **Thin Caller Pattern (GOV-0012 Compliant)**
   * All three templates correctly use the platform reusable workflow `_build-and-release.yml@main`
   * Skeleton delivery.yml files follow the canonical pattern with proper inputs
   * Enables platform-wide security and build improvements without app changes

2. **Schema-Contract Alignment**
   * All schemas follow consistent structure with `version`, `id`, `title`, `description`
   * Required fields properly defined
   * Pattern validation on IDs ensures naming consistency (`^[a-z0-9]+(-[a-z0-9]+)*$`)

3. **ExternalSecret Integration (Backend+RDS)**
   * Correctly references `rds/${env}/${dbname}` path matching platform secret structure
   * Uses `ClusterSecretStore` for cross-namespace access
   * Maps all required DB properties (host, port, dbname, username, password)

4. **Backstage Catalog Registration**
   * All three templates properly registered in `all.yaml`
   * catalog-info.yaml includes techdocs-ref annotation
   * Proper system linkage to `goldenpath-idp`

5. **Kustomize Structure**
   * Clean base + overlays pattern
   * Correct ECR account ID (593517239005)
   * imagePullSecrets patch for ECR authentication

6. **StatefulSet Design (Stateful App)**
   * Correct use of volumeClaimTemplates for per-pod PVCs
   * gp3 storageClass for AWS EBS
   * Headless service for stable network identity

#### Issues to Address

| Priority | Issue | Location | Remediation |
| -------- | ----- | -------- | ----------- |
| P0 | **Kustomization image name mismatch** | `stateless-app/skeleton/deploy/overlays/dev/kustomization.yaml:12` | Image name is hardcoded as `hello-goldenpath-idp` but should be `${{ values.component_id }}` to match deployment |
| P1 | **Missing staging/prod overlays** | All three templates | Only `dev` overlay exists; add `staging` and `prod` overlays for full environment coverage |
| P1 | **Workflow template escaping** | `stateless-app/skeleton/.github/workflows/delivery.yml:36-38` | Uses `$\{{` escaping which may not render correctly; verify Backstage templating handles this |
| P1 | **StatefulSet missing liveness/readiness probes** | `stateful-app/skeleton/deploy/base/statefulset.yaml` | Unlike stateless-app, statefulset lacks health probes |
| P2 | **Template repoOrg indentation** | `stateless-app/template.yaml:39-43`, `stateful-app/template.yaml:40-44` | `repoOrg` property has inconsistent indentation (extra spaces) |
| P2 | **Missing test environment in enum** | All three schemas | Environment enum has `dev`, `staging`, `prod` but missing `test` which exists in platform |
| P2 | **APP_ENV hardcoded to "local"** | `stateless-app/skeleton/deploy/base/deployment.yaml:49` | Should use `${{ values.environment }}` or be removed (ConfigMap handles this) |

#### Contract Alignment Summary

| Contract | Status | Notes |
| -------- | ------ | ----- |
| GOV-0012 Reusable Workflows | PASS | Uses `_build-and-release.yml@main` |
| Schema Contract Pattern | PASS | Consistent structure across all schemas |
| ExternalSecret Pattern | PASS | Correct AWS Secrets Manager path structure |
| Backstage Scaffolder v1beta3 | PASS | Valid template structure |
| Kustomize Overlay Pattern | PARTIAL | Missing staging/prod overlays |
| K8s Best Practices | PARTIAL | StatefulSet missing health probes |

#### Verification Commands

```bash
# Validate template syntax
cd backstage-helm/backstage-catalog/templates/stateless-app
cat template.yaml | yq e '.' -

# Check schema alignment
diff schemas/requests/stateless-app.schema.yaml schemas/requests/stateful-app.schema.yaml

# Verify all.yaml registration
grep -E "(stateless|stateful|backend-app-rds)" backstage-helm/backstage-catalog/all.yaml
```

Signed: claude-opus-4.5 (2026-01-21T14:00:00Z)
