---
id: BACKEND_APP_RDS_REQUEST_FLOW
title: 'How It Works: Backend App + RDS Request Flow'
type: documentation
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - GOLDEN_PATH_OVERVIEW
  - backend-app-rds-template
  - RDS_REQUEST_FLOW
---

# How It Works: Backend App + RDS Request Flow

This document explains the "Golden Path" for provisioning a **Backend Application** that connects to a **Managed RDS Database**. This is the most comprehensive self-service template, combining infrastructure provisioning with application scaffolding.

---

## End-to-End Flow (ASCII)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        BACKSTAGE SCAFFOLDER (Single Form)                       │
│   Developer fills: component_id, databaseName, username, owner, environment     │
└───────────────────────────────────┬─────────────────────────────────────────────┘
                                    │
           ┌────────────────────────┴────────────────────────┐
           │                                                 │
           ▼                                                 ▼
┌─────────────────────────────┐                 ┌─────────────────────────────┐
│    STEP 1: trigger-rds      │                 │    STEP 2: template         │
│    (Infrastructure)         │                 │    (Application Code)       │
│                             │                 │                             │
│  github:actions:dispatch    │                 │  fetch:template             │
│  → create-rds-database.yml  │                 │  → scaffold skeleton/       │
└─────────────┬───────────────┘                 └─────────────┬───────────────┘
              │                                               │
              ▼                                               ▼
┌─────────────────────────────┐                 ┌─────────────────────────────┐
│  Updates in goldenpath-idp: │                 │  Creates App Repo:          │
│                             │                 │                             │
│  • rds-catalog.yaml         │                 │  • .github/workflows/       │
│    (metadata, status)       │                 │      delivery.yml           │
│                             │                 │  • deploy/base/             │
│  • terraform.tfvars         │                 │      externalsecret.yaml    │
│    (application_databases)  │                 │      deployment.yaml        │
│                             │                 │  • deploy/overlays/         │
│  → Creates PR               │                 │      dev/, test/, staging/, │
└─────────────┬───────────────┘                 │      prod/                  │
              │                                 │  • app.py, Dockerfile       │
              │                                 │  • catalog-info.yaml        │
              │                                 └─────────────┬───────────────┘
              │                                               │
              ▼                                               ▼
┌─────────────────────────────┐                 ┌─────────────────────────────┐
│       PR APPROVED           │                 │     REPO PUBLISHED          │
│       & MERGED              │                 │     to GitHub               │
└─────────────┬───────────────┘                 └─────────────┬───────────────┘
              │                                               │
              ▼                                               │
┌─────────────────────────────────────────┐                   │
│          CI TERRAFORM APPLY             │                   │
│                                         │                   │
│  1. terraform apply (creates Secrets    │                   │
│     Manager entry with credentials)     │                   │
│                                         │                   │
│  2. rds_provision.py (auto-invoked)     │                   │
│     • Fetch master creds from SM        │                   │
│     • Connect to Platform RDS           │                   │
│     • CREATE ROLE {username}            │                   │
│     • CREATE DATABASE {dbname}          │                   │
│     • GRANT ALL PRIVILEGES              │                   │
│     • Audit to governance/*.csv         │                   │
└─────────────┬───────────────────────────┘                   │
              │                                               │
              │     ┌─────────────────────────────────────────┘
              │     │
              ▼     ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            RUNTIME (K8s Cluster)                                │
│                                                                                 │
│  ┌─────────────────────┐    ┌─────────────────────┐    ┌──────────────────────┐│
│  │  ExternalSecret     │    │    K8s Secret       │    │    App Deployment    ││
│  │                     │    │                     │    │                      ││
│  │  Watches:           │───▶│  Created:           │───▶│  envFrom:            ││
│  │  goldenpath/{env}/{dbname}/postgres │    │  {app}-db-creds     │    │    secretRef:        ││
│  │                     │    │                     │    │      {app}-db-creds  ││
│  │  refreshInterval:1h │    │  Keys:              │    │                      ││
│  │                     │    │  • DB_HOST          │    │  App has access to:  ││
│  └─────────────────────┘    │  • DB_PORT          │    │  • DB_HOST           ││
│                             │  • DB_NAME          │    │  • DB_PORT           ││
│                             │  • DB_USER          │    │  • DB_NAME           ││
│                             │  • DB_PASS          │    │  • DB_USER           ││
│                             └─────────────────────┘    │  • DB_PASS           ││
│                                                        └──────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## The Composite Pattern

This is a "high-leverage" action. **ONE form submission** triggers **TWO parallel outcomes**:

| Outcome | Mechanism | Result |
|---------|-----------|--------|
| **Infrastructure** | `github:actions:dispatch` → `create-rds-database.yml` | Database + credentials in AWS |
| **Application** | `fetch:template` → `publish:github` | GitHub repo with pre-wired code |

---

## Secret Contract (Zero-Touch)

We use **External Secrets Operator** (ESO) to bridge AWS Secrets Manager and Kubernetes:

```
AWS Secrets Manager                 K8s Cluster
─────────────────────              ─────────────────────

goldenpath/{env}/{dbname}/postgres     ───────▶    ExternalSecret
  │                                    │
  │ Contains:                          │ Watches & Syncs
  │ • host                             │
  │ • port                             ▼
  │ • dbname                       K8s Secret
  │ • username                     {app}-db-creds
  │ • password                         │
                                       │ Mounted by
                                       ▼
                                   Deployment (envFrom)
```

**Secret Path Convention:**
- AWS: `goldenpath/{environment}/{databaseName}/postgres`
- K8s: `{component_id}-db-creds`

---

## Parameters

| Field | Description | Validation | Example |
|-------|-------------|------------|---------|
| **component_id** | App name (becomes repo name) | `^[a-z0-9]+(-[a-z0-9]+)*$` | `user-service` |
| **databaseName** | PostgreSQL database name | `^[a-z][a-z0-9_]{2,62}$` | `users_db` |
| **username** | PostgreSQL role name | `^[a-z][a-z0-9_]{2,30}$` | `users_app_user` |
| **owner** | Team owner (from catalog) | Enum | `platform-team` |
| **environment** | Target environment | `dev`, `test`, `staging`, `prod` | `dev` |

---

## Output Repository Structure

```
{component_id}/
├── .github/workflows/
│   └── delivery.yml              # Thin Caller → _build-and-release.yml@main
├── deploy/
│   ├── base/
│   │   ├── kustomization.yaml    # Resources: deployment, service, externalsecret
│   │   ├── deployment.yaml       # envFrom: secretRef: {app}-db-creds
│   │   ├── service.yaml          # ClusterIP on port 80 → 8080
│   │   └── externalsecret.yaml   # Syncs goldenpath/{env}/{dbname}/postgres → K8s
│   └── overlays/
│       ├── dev/                  # LOG_LEVEL=debug, no TLS
│       ├── test/                 # LOG_LEVEL=debug, no TLS
│       ├── staging/              # LOG_LEVEL=info, TLS staging
│       └── prod/                 # LOG_LEVEL=warn, TLS prod
├── app.py                        # Python skeleton with DB health check
├── Dockerfile                    # Python 3.11 slim
├── requirements.txt              # Flask, psycopg2-binary, gunicorn
├── catalog-info.yaml             # Backstage registration
└── README.md                     # Auto-generated docs
```

---

## CI/CD Integration (GOV-0012)

All scaffolded apps use the **Thin Caller Pattern**:

```yaml
# App repo: .github/workflows/delivery.yml
jobs:
  build:
    uses: mikeybeezy/goldenpath-idp-infra/.github/workflows/_build-and-release.yml@main
    with:
      ecr_repository: ${{ values.component_id }}
    secrets:
      AWS_ROLE_ARN: ${{ secrets.AWS_ROLE_ARN }}
```

**Security Gates Applied:**
- Gitleaks secret scan (advisory in dev, blocking in test+)
- Trivy vulnerability scan (blocking HIGH/CRITICAL in test+)
- SBOM generation (required in test+)

---

## RDS Provisioning Automation

The `rds_provision.py` script runs automatically after Terraform apply:

```
┌─────────────────────────────────────────────────────────────┐
│                    rds_provision.py                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Parse application_databases from terraform.tfvars      │
│                                                             │
│  2. For each app:                                           │
│     a. Fetch app password from Secrets Manager              │
│        goldenpath/{env}/{app}/postgres                      │
│                                                             │
│     b. Connect to Platform RDS (master creds)               │
│                                                             │
│     c. Execute idempotent SQL:                              │
│        • CREATE ROLE IF NOT EXISTS                          │
│        • ALTER ROLE ... PASSWORD (if exists)                │
│        • CREATE DATABASE IF NOT EXISTS                      │
│        • GRANT ALL PRIVILEGES                               │
│                                                             │
│     d. Record audit entry                                   │
│                                                             │
│  3. Persist audit to governance/{env}/rds_provision_audit   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Makefile Targets:**
```bash
make rds-provision ENV=dev              # Manual provision
make rds-provision-dry-run ENV=dev      # Preview changes
make rds-provision-auto ENV=dev         # Auto-detect mode (standalone/coupled)
```

---

## Comparison: Golden Path Templates

| Aspect | stateless-app | stateful-app | backend-app-rds |
|--------|---------------|--------------|-----------------|
| **Workload** | Deployment | StatefulSet | Deployment |
| **State** | None | EBS PVC | RDS PostgreSQL |
| **Durability** | N/A | Single AZ | Multi-AZ (managed) |
| **Secrets** | None | None | ExternalSecret |
| **Infra Trigger** | None | None | `create-rds-database.yml` |

---

## Related Documentation

- [RDS Request Flow](./RDS_REQUEST_FLOW.md) - Detailed RDS provisioning lifecycle
- [Golden Path Overview](./GOLDEN_PATH_OVERVIEW.md) - Template comparison
- [GOV-0012: Build Pipeline Standards](../../10-governance/policies/GOV-0012-build-pipeline-standards.md)
- [Platform RDS Architecture](../../70-operations/30_PLATFORM_RDS_ARCHITECTURE.md)
- [ADR-0165: RDS User/DB Provisioning Automation](../../adrs/ADR-0165-rds-user-db-provisioning-automation.md)
