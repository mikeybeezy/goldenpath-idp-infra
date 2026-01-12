---
id: 18_BACKSTAGE_MVP
title: Backstage MVP (First App Through CI/CD)
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
  - 03_GOVERNANCE_BACKSTAGE
  - 12_GITOPS_AND_CICD
  - ADR-0008
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# Backstage MVP (First App Through CI/CD)

Doc contract:

- Purpose: Define the minimum Backstage path to validate CI, GitOps, and ingress.
- Owner: platform
- Status: reference
- Review cadence: as needed
- Related: docs/10-governance/03_GOVERNANCE_BACKSTAGE.md, docs/40-delivery/12_GITOPS_AND_CICD.md, docs/adrs/ADR-0008-app-backstage-portal.md

This is the minimal path to prove the platform end‑to‑end: build an app, ship
an image, deploy via GitOps, and expose it through Kong.

## Scope (V1 MVP)

- Minimal Backstage install (catalog + scaffolder + techdocs only).
- CI builds + pushes a single image tag per build.
- GitOps deploys that image via Argo CD.
- Kong routes external traffic to Backstage.

## Checklist

### 1) Scaffold Backstage

- Create the repo via the app scaffolder (Backstage template or workflow).
- Keep plugins minimal (catalog, scaffolder, techdocs).
- Add a simple health endpoint in the backend.

### 2) Containerize

- Add Dockerfile and local docker‑compose for dev.
- Use one image tag per build (build ID or git SHA).

### 3) CI build + push

- Build image and push to your registry.
- Emit the image tag as a build output.
- Keep secrets in CI (registry credentials only).

### 4) GitOps deploy

- Add or update an Argo CD app for Backstage:
  - `gitops/argocd/apps/<env>/backstage.yaml`
- Use environment values files:
  - `gitops/helm/backstage/values/<env>.yaml`

### 5) Ingress

- Route through Kong (single external entrypoint).
- Confirm `/` and `/api` are reachable.

### 6) Validate

- Argo CD app shows `Synced/Healthy`.
- Backstage pods are `Ready`.
- Kong route responds (HTTP 200).

## Files to touch (current repo)

- GitOps app: `gitops/argocd/apps/<env>/backstage.yaml`
- Helm values: `gitops/helm/backstage/values/<env>.yaml`
- CI stub: `.github/workflows/ci-backstage.yml`

## Notes

- Auth can remain disabled for MVP; Keycloak is a later integration step.
- Keep the first delivery small so we can validate CI → GitOps → Kong quickly.
