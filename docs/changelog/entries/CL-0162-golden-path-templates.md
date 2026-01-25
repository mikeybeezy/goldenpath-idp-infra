<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: CL-0162
title: Golden Path Templates for Self-Service App Scaffolding
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to:
  - backstage-helm/backstage-catalog/templates/stateless-app/**
  - backstage-helm/backstage-catalog/templates/stateful-app/**
  - backstage-helm/backstage-catalog/templates/backend-app-rds/**
  - schemas/requests/stateless-app.schema.yaml
  - schemas/requests/stateful-app.schema.yaml
  - schemas/requests/backend-app-rds.schema.yaml
  - scripts/rds_request_parser.py
lifecycle: active
exempt: false
risk_profile:
  production_impact: medium
  security_risk: low
  coupling_risk: medium
schema_version: 1
relates_to:
  - session-2026-01-21-scaffold-golden-paths
  - GOV-0012-build-pipeline-standards
  - GOLDEN_PATH_OVERVIEW
  - STATELESS_APP_REQUEST_FLOW
  - STATEFUL_APP_REQUEST_FLOW
  - BACKEND_APP_RDS_REQUEST_FLOW
supersedes: []
superseded_by: []
tags:
  - backstage
  - scaffolder
  - golden-path
  - self-service
inheritance: {}
supported_until: 2028-01-21
value_quantification:
  vq_class: HV/LQ
  impact_tier: high
  potential_savings_hours: 40.0
date: 2026-01-21
author: platform-team
---

# Golden Path Templates for Self-Service App Scaffolding

## Summary

Added three Backstage Scaffolder templates enabling developers to self-service provision production-ready applications with a single form submission. Each template creates a GitHub repository with application code, CI/CD pipeline, Kubernetes manifests, and governance metadata.

## What Changed

### New Templates

| Template | Workload | State | Use Case |
|----------|----------|-------|----------|
| **stateless-app** | Deployment | None | APIs, web services, microservices |
| **stateful-app** | StatefulSet + PVC | Local (EBS) | Caches, queues, search indices |
| **backend-app-rds** | Deployment + RDS | Managed DB | Business-critical data apps |

### Repository Created on Scaffold

Each template creates a GitHub repository containing:

```
{component_id}/
├── .github/workflows/
│   └── delivery.yml          # Thin Caller → _build-and-release.yml@main
├── deploy/
│   ├── base/                 # K8s manifests (Deployment/StatefulSet, Service)
│   └── overlays/             # dev, test, staging, prod configurations
│       ├── dev/
│       ├── test/
│       ├── staging/
│       └── prod/
├── app.py                    # Application code skeleton
├── Dockerfile                # Container definition
├── catalog-info.yaml         # Backstage registration
└── README.md                 # Documentation
```

### CI/CD Integration (GOV-0012 Compliant)

All scaffolded apps use the **Thin Caller Pattern**:

- App repo contains minimal `delivery.yml` (~20 lines)
- Calls canonical `_build-and-release.yml@main` from platform repo
- Inherits security gates: Gitleaks, Trivy, SBOM generation
- Environment-aware gating: Advisory (dev) → Blocking (test/staging/prod)

### Environment Overlays

| Environment | LOG_LEVEL | TLS | Domain Pattern |
|-------------|-----------|-----|----------------|
| dev | debug | No | `{app}.dev.goldenpathidp.io` |
| test | debug | No | `{app}.test.goldenpathidp.io` |
| staging | info | letsencrypt-staging | `{app}.staging.goldenpathidp.io` |
| prod | warn | letsencrypt-prod | `{app}.goldenpathidp.io` |

### StatefulSet Special Handling

The stateful-app template includes:

- **Headless Service** (`service-headless.yaml`) for pod-to-pod communication
- **Load-Balancer Service** (`service.yaml` in overlays) for external access
- **volumeClaimTemplates** for automatic PVC provisioning (gp3 StorageClass)
- Liveness and readiness probes

### Backend + RDS Special Handling

The backend-app-rds template includes:

- **ExternalSecret** for zero-touch AWS Secrets Manager → K8s Secret sync
- Secret path convention: `goldenpath/{env}/{dbname}/postgres`
- Database credentials injected via `envFrom`

## Files Added

- `backstage-helm/backstage-catalog/templates/stateless-app/**`
- `backstage-helm/backstage-catalog/templates/stateful-app/**`
- `backstage-helm/backstage-catalog/templates/backend-app-rds/**`
- `schemas/requests/stateless-app.schema.yaml`
- `schemas/requests/stateful-app.schema.yaml`
- `schemas/requests/backend-app-rds.schema.yaml`
- `docs/85-how-it-works/self-service/GOLDEN_PATH_OVERVIEW.md`

## Files Modified

- `backstage-helm/backstage-catalog/all.yaml` (registered new templates)
- `docs/85-how-it-works/README.md` (added Golden Path section)
- `docs/85-how-it-works/self-service/STATEFUL_APP_REQUEST_FLOW.md` (enhanced)

## Value Delivered

- **Developer Experience**: One-click app provisioning (estimated 4-8 hours saved per app)
- **Consistency**: All apps follow same patterns, security gates, and governance
- **Maintainability**: Platform updates (security, build) propagate to all apps automatically
- **Compliance**: Born governed with catalog-info.yaml and metadata from day 0

## Verification

```bash
# Verify templates registered in Backstage catalog
grep -E "(stateless|stateful|backend-app-rds)" backstage-helm/backstage-catalog/all.yaml

# Verify overlay directories exist
ls backstage-helm/backstage-catalog/templates/*/skeleton/deploy/overlays/

# Verify thin caller pattern in delivery.yml
grep "_build-and-release.yml" backstage-helm/backstage-catalog/templates/*/skeleton/.github/workflows/delivery.yml
```

## Related Documentation

- [Golden Path Overview](../../85-how-it-works/self-service/GOLDEN_PATH_OVERVIEW.md)
- [Stateless App Request Flow](../../85-how-it-works/self-service/STATELESS_APP_REQUEST_FLOW.md)
- [Stateful App Request Flow](../../85-how-it-works/self-service/STATEFUL_APP_REQUEST_FLOW.md)
- [Backend App + RDS Request Flow](../../85-how-it-works/self-service/BACKEND_APP_RDS_REQUEST_FLOW.md)
- [GOV-0012 Build Pipeline Standards](../../10-governance/policies/GOV-0012-build-pipeline-standards.md)
