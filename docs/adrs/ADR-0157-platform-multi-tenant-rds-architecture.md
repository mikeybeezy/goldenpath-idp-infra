<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: ADR-0157-platform-multi-tenant-rds-architecture
title: 'ADR-0157: Multi-Tenant RDS for Platform Tooling Applications'
type: adr
status: superseded
domain: platform-core
value_quantification:
  vq_class: 🟢 HV/HQ
  impact_tier: high
  potential_savings_hours: 40.0
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: terraform-destroy
  observability_tier: silver
schema_version: 1
relates_to:
  - 01_adr_index
  - 35_TOOLING_SECRETS_LIFECYCLE
  - ADR-0006-platform-secrets-strategy
  - ADR-0007-platform-environment-model
  - ADR-0053-platform-storage-lifecycle-separation
  - ADR-0157-platform-multi-tenant-rds-architecture
  - ADR-0158-platform-standalone-rds-bounded-context
  - ADR-0160
supersedes: []
superseded_by:
  - ADR-0158
tags:
  - rds
  - database
  - keycloak
  - backstage
  - multi-tenant
inheritance: {}
supported_until: 2028-01-15
version: 1.0
breaking_change: false
---

## ADR-0157: Multi-Tenant RDS for Platform Tooling Applications

- **Status:** Superseded (by ADR-0158)
- **Date:** 2026-01-15
- **Owners:** Platform Team
- **Domain:** Platform
- **Decision type:** Architecture / Operations / Cost
- **Related:** ADR-0006 (Secrets Strategy), ADR-0007 (Environment Model), ADR-0053 (Storage Lifecycle)

---

## Context

Platform tooling applications (Keycloak, Backstage) require persistent PostgreSQL databases. Three options exist:

1. **Bundled PostgreSQL** - Each app deploys its own PostgreSQL container
2. **Dedicated RDS per app** - Each app gets its own RDS instance
3. **Shared multi-tenant RDS** - Single RDS instance with separate databases per app

Constraints:

- Cost efficiency is critical for dev/ephemeral environments
- Data must survive cluster teardown (ADR-0006 principle)
- Secrets must be auto-generated and stored in AWS Secrets Manager
- Ephemeral builds require unique, suffixed resource names (build_id pattern)
- Each component must be deployable as a separate Terraform resource

---

## Decision

We will use a **shared multi-tenant RDS PostgreSQL instance** for platform tooling applications with the following architecture:

1. **Single RDS instance** (`goldenpath-platform-db`) hosts multiple logical databases
2. **Separate database and user per application** (keycloak, backstage)
3. **Auto-generated credentials** stored in AWS Secrets Manager per application
4. **ExternalSecrets** syncs credentials to Kubernetes for apps to consume
5. **RDS deployed before EKS** in the Terraform apply sequence

### Resource Naming

|Environment|RDS Identifier|
|-------------|----------------|
|Persistent (dev/staging/prod)|`goldenpath-platform-db`|
|Ephemeral|`goldenpath-platform-db-{build_id}`|

### Secret Paths

|Application|Secret Path|Contents|
|-------------|-------------|----------|
|Master|`goldenpath/{env}/platform-db/master`|Master credentials|
|Keycloak|`goldenpath/{env}/keycloak/postgres`|App-specific credentials|
|Backstage|`goldenpath/{env}/backstage/postgres`|App-specific credentials|

---

## Scope

### Applies to

- Platform tooling apps: Keycloak, Backstage
- All environments: dev, staging, prod, ephemeral

### Does not apply to

- Application workloads (tenant apps use their own databases)
- Local development (uses bundled PostgreSQL)
- Observability stack (uses filesystem/object storage)

---

## Consequences

### Positive

- **Cost reduction**: Single `db.t3.micro` vs multiple instances (~60% savings)
- **Operational simplicity**: One RDS to monitor, backup, patch
- **Secrets automation**: Credentials auto-generated, no manual creation
- **Rebuild resilience**: Data survives cluster teardown
- **Consistent patterns**: Same approach for all tooling apps

### Tradeoffs / Risks

- **Blast radius**: RDS failure affects all tooling apps
- **Resource contention**: Apps share CPU/memory/IOPS
- **Security boundary**: Logical separation only (same instance)
- **Tight coupling**: Coordinated maintenance windows

### Mitigations

- Enable Multi-AZ for production environments
- Use Performance Insights for contention monitoring
- Separate credentials per app (no shared passwords)
- Deletion protection enabled in production

### Operational Impact

- Terraform must apply RDS **before** EKS cluster
- ExternalSecrets Operator must be deployed before apps
- App helm values must reference ExternalSecrets, not bundled PostgreSQL

---

## Deployment Sequence

RDS and secrets must be provisioned **before** the EKS cluster and tooling apps:

```text
Phase 0: Pre-cluster Infrastructure
├── VPC, Subnets, Security Groups
├── RDS Instance (goldenpath-platform-db)
├── Secrets Manager secrets (auto-generated)
└── IAM roles (ESO, IRSA)

Phase 1: EKS Cluster
├── EKS control plane
├── Node groups
└── EKS addons (EBS CSI, etc.)

Phase 2: Platform Bootstrap
├── External Secrets Operator
├── ClusterSecretStore (aws-secretsmanager)
└── ExternalSecrets (keycloak-postgres-secret, backstage-postgres-secret)

Phase 3: Tooling Apps
├── Keycloak (uses external RDS)
├── Backstage (uses external RDS)
└── Kong, ArgoCD, Monitoring
```

---

## Alternatives Considered

### 1. Bundled PostgreSQL (StatefulSet per app)

- **Pros**: Simple, no AWS dependency, works locally
- **Cons**: Data lost on cluster teardown, manual backup, no HA
- **Verdict**: Suitable for local dev only

### 2. Dedicated RDS per app

- **Pros**: Full isolation, independent scaling
- **Cons**: 2-3x cost, operational overhead
- **Verdict**: Overkill for platform tooling

### 3. Aurora Serverless v2

- **Pros**: Auto-scaling, pay-per-use
- **Cons**: Higher baseline cost, complexity
- **Verdict**: Consider for production scale

---

## Follow-ups

- [ ] Document RDS module in `modules/aws_rds/README.md`
- [ ] Add CloudWatch alarms for RDS (CPU, connections, storage)
- [ ] Define backup/restore runbook
- [ ] Enable Multi-AZ for staging/prod environments
- [ ] Add Performance Insights dashboard to Grafana

---

## Notes

- For local development, apps use bundled PostgreSQL via `local.yaml` values
- Keycloak admin password is a separate secret (`goldenpath/{env}/keycloak/admin`)
- Database users are created at RDS provisioning; schema created by apps on first boot
- Consider Aurora Serverless v2 if production load exceeds `db.t3.small` capacity
