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
