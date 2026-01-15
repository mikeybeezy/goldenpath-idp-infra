---
id: RDS_REQUEST_FLOW
title: 'How It Works: RDS Database Request Flow'
type: documentation
relates_to:
  - docs/adrs/ADR-0158-platform-standalone-rds-bounded-context.md
  - .github/workflows/create-rds-database.yml
  - backstage-helm/backstage-catalog/templates/rds-request.yaml
  - docs/70-operations/30_PLATFORM_RDS_ARCHITECTURE.md
---

# How It Works: RDS Database Request Flow

This document explains the technical lifecycle of an RDS database request, from the developer form in Backstage to credential availability in AWS Secrets Manager.

## 0. High-Level Architecture

The platform uses a "Bounded Context" approach to RDS provisioning. The Platform RDS is a shared PostgreSQL instance that hosts isolated databases for multiple applications, with dedicated credentials per database.

```text
+---------------+       +-----------------------+
|   Backstage   | ----> | GitHub Actions Dispatch|
+---------------+       +-----------------------+
                                   |
                       ( 1. Validate inputs )
                                   |
           +-----------------------+-------+-----------------------+
           |                               |                       |
+-----------------------+       +-----------------------+   +-----------------------+
|  Update RDS Catalog   |       | Update env-rds tfvars |   |  Generate PR Body     |
+-----------------------+       +-----------------------+   +-----------------------+
           |                               |                       |
           +-----------------------+-------+-----------------------+
                                   |
                         ( 2. Create PR )
                                   |
+-----------------------+          |
|  Platform Approval    | <--------+ (PR Merged)
+-----------------------+
       |
       |       +---------------------------------------+
       +-----> | make rds-apply ENV={env}              |
               +---------------------------------------+
                               |
               +---------------+---------------+
               |                               |
       +---------------+             +-------------------+
       | PostgreSQL DB |             | AWS Secrets Mgr   |
       +---------------+             +-------------------+
```

## 1. Trigger: Backstage Template

Application teams use the **"Request Platform RDS Database"** template in the Backstage Software Catalog. The template collects:

| Field | Description | Example |
|-------|-------------|---------|
| `database_name` | Logical database name | `inventory_service` |
| `username` | Database user | `inventory_user` |
| `owner` | Owning team | `app-team` |
| `requester` | Requesting user | `daniel-deans` |
| `environment` | Target environment | `dev`, `staging`, `prod` |
| `domain` | Business domain | `application` |
| `risk` | Data classification | `low`, `medium`, `high` |

The template triggers `create-rds-database.yml` via `github:actions:dispatch`.

## 2. Processing: Workflow Execution

The GitHub Actions workflow performs three key operations:

### 2.1 Input Validation

```bash
# Database name: lowercase, underscores, starts with letter
^[a-z][a-z0-9_]*$

# Username: same pattern
^[a-z][a-z0-9_]*$

# Requester: lowercase alphanumeric with dashes
^[a-z0-9-]+$
```

### 2.2 Catalog Update (Idempotent)

Updates `docs/20-contracts/resource-catalogs/rds-catalog.yaml` using `yq`:

```yaml
databases:
  inventory_service:
    metadata:
      id: DATABASE_INVENTORY_SERVICE
      owner: app-team
      requested_by: daniel-deans
      domain: application
      risk: medium
      environment: dev
      status: pending
      created_date: "2026-01-15"
    configuration:
      username: inventory_user
      secret_path: goldenpath/dev/inventory_service/postgres
```

### 2.3 Terraform tfvars Update

Injects entry into `envs/{env}-rds/terraform.tfvars`:

```hcl
application_databases = {
  # ... existing databases ...

  inventory_service = {
    database_name = "inventory_service"
    username      = "inventory_user"
  }
}
```

## 3. Review: Pull Request

The workflow creates a PR with comprehensive details:

- Database and user configuration
- Platform RDS instance details
- Risk-based security controls (auto-applied)
- Step-by-step "What Happens Next" guide
- Links to architecture docs and runbooks

### Risk-Based Security Controls

| Risk Level | Backup Retention | Secret Rotation | Additional Controls |
|------------|------------------|-----------------|---------------------|
| Low | 7 days | 30 days | Basic monitoring |
| Medium | 14 days | 30 days | Standard monitoring |
| High | 35 days | 14 days | Audit logging, enhanced monitoring |

## 4. Execution: Terraform Apply

After PR approval and merge, the platform team runs:

```bash
make rds-apply ENV=dev
```

This executes the Terraform configuration which:

1. Creates the PostgreSQL database on the shared RDS instance
2. Creates the database user with appropriate privileges
3. Generates a secure random password
4. Stores credentials in AWS Secrets Manager

## 5. Credential Access

### AWS Secrets Manager

Credentials are stored at:

```text
goldenpath/{env}/{database_name}/postgres
```

Secret structure:

```json
{
  "username": "inventory_user",
  "password": "<generated>",
  "host": "goldenpath-platform-db-dev.xxxxx.us-west-2.rds.amazonaws.com",
  "port": "5432",
  "dbname": "inventory_service"
}
```

### Kubernetes Access (via ExternalSecrets)

Teams can sync credentials to their namespace using ExternalSecrets Operator:

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: inventory-postgres-secret
  namespace: inventory-service
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: ClusterSecretStore
  target:
    name: inventory-postgres-secret
  data:
    - secretKey: POSTGRES_USER
      remoteRef:
        key: goldenpath/dev/inventory_service/postgres
        property: username
    - secretKey: POSTGRES_PASSWORD
      remoteRef:
        key: goldenpath/dev/inventory_service/postgres
        property: password
    - secretKey: POSTGRES_HOST
      remoteRef:
        key: goldenpath/dev/inventory_service/postgres
        property: host
```

## 6. Lifecycle: Secret Rotation

### CI Enforcement

The platform enforces rotation via two mechanisms:

1. **Daily Alert** (`secret-rotation-check.yml`): Creates GitHub issues when secrets approach or exceed rotation deadline
2. **PR Soft Gate** (`pr-secret-rotation-warning.yml`): Posts warning comments on infrastructure PRs (non-blocking)

### Manual Rotation Procedure

See [RB-0029: Manual Secret Rotation](../../70-operations/runbooks/RB-0029-rds-manual-secret-rotation.md)

## 7. Summary: The Value Loop

By abstracting the complexity of shared RDS management, the platform provides:

| Benefit | Description |
|---------|-------------|
| **Zero Bottlenecks** | Teams request databases without waiting for DBAs |
| **100% Governance** | Every database is tagged with owner, domain, and risk |
| **Credential Isolation** | Each database has dedicated credentials |
| **Cost Efficiency** | Shared RDS instance reduces infrastructure overhead |
| **Data Persistence** | RDS survives cluster rebuilds (bounded context) |
| **Rotation Compliance** | CI-enforced secret rotation deadlines |

## Related Documentation

- [ADR-0158: Platform Standalone RDS Bounded Context](../../adrs/ADR-0158-platform-standalone-rds-bounded-context.md)
- [Platform RDS Architecture](../../70-operations/30_PLATFORM_RDS_ARCHITECTURE.md)
- [RB-0029: Manual Secret Rotation](../../70-operations/runbooks/RB-0029-rds-manual-secret-rotation.md)
- [RB-0030: Break-Glass Deletion](../../70-operations/runbooks/RB-0030-rds-break-glass-deletion.md)
