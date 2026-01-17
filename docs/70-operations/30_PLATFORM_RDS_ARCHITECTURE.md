---
id: 30_PLATFORM_RDS_ARCHITECTURE
title: Platform RDS Architecture
---

## Platform RDS Architecture

This living document describes the standalone RDS PostgreSQL bounded context for platform tooling applications.

**ADR Reference:** [ADR-0158: Platform Standalone RDS Bounded Context](../adrs/ADR-0158-platform-standalone-rds-bounded-context.md)

## Overview

Platform tooling applications (Keycloak, Backstage) share a single RDS PostgreSQL instance with logical database separation. RDS is deployed as a **standalone bounded context** with its own Terraform root, separate from EKS cluster state.

### Deployment Modes (Coexist)

The platform supports **both** modes:

| Mode | Terraform root | Trigger | Use case |
| --- | --- | --- | --- |
| Coupled RDS | `envs/<env>/` | EKS apply/build | Standard platform builds |
| Standalone RDS | `envs/<env>-rds/` | Backstage request + approval | Team-requested persistence |

### Key Principles

- **Persistent**: RDS survives cluster rebuilds
- **Separate State**: Own Terraform root (`envs/{env}-rds/`)
- **Protected**: Multiple layers prevent accidental deletion
- **Region Agnostic**: No hardcoded regions

```text
┌─────────────────────────────────────────────────────────────┐
│                    AWS Secrets Manager                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ .../keycloak/   │  │ .../backstage/  │  │ .../master   │ │
│  │    postgres     │  │    postgres     │  │              │ │
│  └────────┬────────┘  └────────┬────────┘  └──────────────┘ │
└───────────┼────────────────────┼────────────────────────────┘
            │                    │
            ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│              External Secrets Operator (ESO)                 │
│         ClusterSecretStore: aws-secretsmanager               │
└───────────┬────────────────────┬────────────────────────────┘
            │                    │
            ▼                    ▼
┌─────────────────┐    ┌─────────────────┐
│ keycloak-       │    │ backstage-      │
│ postgres-secret │    │ postgres-secret │
│ (K8s Secret)    │    │ (K8s Secret)    │
└────────┬────────┘    └────────┬────────┘
         │                      │
         ▼                      ▼
┌─────────────────┐    ┌─────────────────┐
│    Keycloak     │    │    Backstage    │
│   (Helm App)    │    │   (Helm App)    │
└────────┬────────┘    └────────┬────────┘
         │                      │
         └──────────┬───────────┘
                    ▼
┌─────────────────────────────────────────────────────────────┐
│                  RDS PostgreSQL Instance                     │
│                  goldenpath-platform-db                      │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │ Database:       │  │ Database:       │                   │
│  │ keycloak        │  │ backstage       │                   │
│  │ User: keycloak  │  │ User: backstage │                   │
│  └─────────────────┘  └─────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

## Deployment Sequence

RDS must be deployed **before** the EKS cluster because:

1. Secrets are generated at RDS creation time
2. ExternalSecrets need secrets to exist in AWS before syncing
3. Apps need database connectivity on first boot

### Makefile Commands

#### Coupled RDS (Standard EKS Build)

```bash
# 1. Deploy EKS + coupled RDS
make apply ENV=dev BUILD_ID=xx-xx-xx-xx

# 2. Provision database roles + users (mode detection)
make rds-provision-auto ENV=dev BUILD_ID=xx-xx-xx-xx

# 3. Bootstrap platform
make bootstrap ENV=dev BUILD_ID=xx-xx-xx-xx
```

#### Deploy Shortcut (Apply + Bootstrap)

```bash
# Single-command deploy (apply + bootstrap + verify)
make deploy ENV=dev BUILD_ID=xx-xx-xx-xx
```

Note: `make deploy` does not yet insert `rds-provision-auto`. Until that is
wired into `deploy`, use the explicit three-step sequence above when RDS is
required for platform apps.

#### Standalone RDS (Persistent Layer)

```bash
# 1. Deploy RDS first (separate Terraform root)
make rds-init ENV=dev
make rds-plan ENV=dev
make rds-apply ENV=dev

# 2. Then deploy EKS cluster
make apply ENV=dev BUILD_ID=xx-xx-xx-xx

# 3. Then provision DB roles/users (mode detection)
make rds-provision-auto ENV=dev RDS_MODE=standalone BUILD_ID=xx-xx-xx-xx

# 4. Then bootstrap
make bootstrap ENV=dev BUILD_ID=xx-xx-xx-xx
```

### Full Deployment Order

```text
┌──────────────────────────────────────────────────────────────┐
│ PHASE 0: Platform RDS (Standalone Terraform Root)            │
│ ─────────────────────────────────────────────────────────────│
│ Location: envs/dev-rds/                                      │
│                                                              │
│ make rds-apply ENV=dev                                       │
│                                                              │
│ Creates:                                                     │
│ - RDS Instance with deletion_protection=true                 │
│ - DB Subnet Group                                            │
│ - Security Group (5432 from VPC CIDR)                        │
│ - Parameter Group (SSL required)                             │
│ - Secrets in AWS Secrets Manager                             │
│ - CloudWatch Alarms                                          │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│ PHASE 1: EKS Cluster (Main Terraform Root)                   │
│ ─────────────────────────────────────────────────────────────│
│ Location: envs/dev/                                          │
│                                                              │
│ make apply ENV=dev BUILD_ID=xx-xx-xx-xx                      │
│                                                              │
│ Creates:                                                     │
│ - VPC + Subnets (if not existing)                            │
│ - EKS Control Plane                                          │
│ - Node Groups                                                │
│ - OIDC Provider                                              │
│ - IAM Roles (ESO, IRSA, LB Controller)                       │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│ PHASE 2: Platform Bootstrap (ArgoCD / Helm)                  │
│ ─────────────────────────────────────────────────────────────│
│ make bootstrap ENV=dev                                       │
│                                                              │
│ 1. ArgoCD                                                    │
│ 2. External Secrets Operator                                 │
│ 3. ClusterSecretStore (aws-secretsmanager)                   │
│ 4. cert-manager                                              │
│ 5. Kong Ingress Controller                                   │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│ PHASE 3: Tooling Apps (ArgoCD Applications)                  │
│ ─────────────────────────────────────────────────────────────│
│ 1. ExternalSecrets (keycloak-postgres-secret, etc.)          │
│ 2. Keycloak ◄─── Reads from keycloak-postgres-secret         │
│ 3. Backstage ◄─── Reads from backstage-postgres-secret       │
│ 4. Monitoring Stack (Prometheus, Grafana, Loki)              │
└──────────────────────────────────────────────────────────────┘
```

## Terraform Configuration

### Directory Structure

```text
envs/
├── dev/                    # EKS cluster (ephemeral)
│   ├── main.tf
│   ├── variables.tf
│   └── terraform.tfvars
└── dev-rds/                # Platform RDS (persistent)
    ├── main.tf             # RDS instance, security, secrets
    ├── variables.tf        # Region-agnostic configuration
    ├── outputs.tf          # For debugging only
    └── terraform.tfvars    # Environment-specific values
```

### VPC Discovery

RDS discovers the VPC via tags rather than direct Terraform reference:

```hcl
# envs/dev-rds/main.tf
data "aws_vpc" "platform" {
  filter {
    name   = "tag:Project"
    values = ["goldenpath-idp"]
  }
  filter {
    name   = "tag:Environment"
    values = [local.environment]
  }
}
```

### Deletion Protection

Multiple layers prevent accidental deletion:

```hcl
resource "aws_db_instance" "platform" {
  # AWS-level protection
  deletion_protection = true

  # Terraform-level protection
  lifecycle {
    prevent_destroy = true
  }
}
```

## Secrets Management

### Secret Generation

Secrets are **auto-generated** by Terraform at RDS creation time:

|Secret|Generated By|Contents|
|--------|--------------|----------|
|Master credentials|`random_password.master`|32-char alphanumeric|
|App credentials|`random_password.app[*]`|32-char alphanumeric per app|

### Secret Storage Paths

|Application|AWS Secret Path|K8s Secret Name|
|-------------|-----------------|-----------------|
|Master|`goldenpath/{env}/rds/master`|N/A (not synced)|
|Keycloak|`goldenpath/{env}/keycloak/postgres`|`keycloak-postgres-secret`|
|Backstage|`goldenpath/{env}/backstage/postgres`|`backstage-postgres-secret`|

### Secret Rotation

V1 uses manual rotation with CI enforcement:

- Daily scheduled workflow alerts when secrets > 25 days old
- PR soft gate warns (non-blocking) when approaching deadline
- Runbook: [RB-0029 Manual Secret Rotation](runbooks/RB-0029-rds-manual-secret-rotation.md)

#### Rotation Policy

|Environment|Rotation Period|Warning Threshold|
|-----------|---------------|-----------------|
|Dev|30 days|5 days before|
|Staging|14 days|5 days before|
|Production|14 days|5 days before|

## Environment-Specific Settings

|Setting|Dev|Staging|Production|
|-------------------|-----------|-----------|-------------|
|Instance Class|db.t3.micro|db.t3.small|db.t3.medium+|
|Multi-AZ|false|true|true|
|Deletion Protection|true|true|true|
|Skip Final Snapshot|false|false|false|
|Backup Retention|7 days|14 days|35 days|
|Storage Autoscaling|20-50 GB|20-100 GB|50-500 GB|
|Secret Rotation|30 days|14 days|14 days|

## CloudWatch Alarms

The following alarms are created automatically:

|Alarm|Warning|Critical|
|--------------------|--------|--------|
|CPU Utilization|>70%|>90%|
|Freeable Memory|<512MB|<256MB|
|Free Storage|<30%|<15%|
|Database Connections|>70% max|N/A|
|Read Latency|>50ms|N/A|
|Write Latency|>50ms|N/A|

## Troubleshooting

### Secret Not Syncing

```bash
# Check ExternalSecret status
kubectl get externalsecret -n keycloak keycloak-postgres-secret -o yaml

# Check ClusterSecretStore
kubectl get clustersecretstore aws-secretsmanager -o yaml

# Verify secret exists in AWS
aws secretsmanager get-secret-value \
  --secret-id goldenpath/dev/keycloak/postgres \
  --query SecretString --output text | jq .
```

### App Cannot Connect to RDS

```bash
# Check security group allows EKS nodes
aws ec2 describe-security-groups --group-ids sg-xxx

# Test connectivity from pod
kubectl run pg-test --rm -it --image=postgres:15 -- \
  psql -h <rds-endpoint> -U keycloak -d keycloak
```

### RDS Status

```bash
# Check RDS outputs
make rds-status ENV=dev

# Or directly via Terraform
cd envs/dev-rds && terraform output
```

## Deletion Procedure

RDS cannot be destroyed via Terraform or Makefile. Deletion requires manual console intervention.

**Runbook:** [RB-0030 RDS Break-Glass Deletion](runbooks/RB-0030-rds-break-glass-deletion.md)

## Related Documentation

- [ADR-0158: Platform Standalone RDS Bounded Context](../adrs/ADR-0158-platform-standalone-rds-bounded-context.md)
- [Tooling Secrets Lifecycle](35_TOOLING_SECRETS_LIFECYCLE.md)
- [Tooling Apps Matrix](20_TOOLING_APPS_MATRIX.md)
- [Local Development](25_LOCAL_DEVELOPMENT.md)
- [RB-0029: Manual Secret Rotation](runbooks/RB-0029-rds-manual-secret-rotation.md)
- [RB-0030: RDS Break-Glass Deletion](runbooks/RB-0030-rds-break-glass-deletion.md)
