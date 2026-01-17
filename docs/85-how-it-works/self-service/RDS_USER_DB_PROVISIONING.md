---
id: RDS_USER_DB_PROVISIONING
title: 'How It Works: RDS User and Database Provisioning'
type: documentation
relates_to:
  - 30_PLATFORM_RDS_ARCHITECTURE
  - ADR-0158-platform-standalone-rds-bounded-context
  - ADR-0165
  - PRD-0001-rds-user-db-provisioning
  - RB-0032
  - RDS_DUAL_MODE_AUTOMATION
  - RDS_REQUEST_FLOW
  - SCRIPT-0035
  - agent_session_summary
tags:
  - rds
  - provisioning
  - automation
  - how-it-works
  - federation
---

# How It Works: RDS User and Database Provisioning

This document explains how the platform automatically creates PostgreSQL users and databases, the architectural decisions behind it, and how it scales across clusters and VPCs.

## Quick Summary

| Question | Answer |
| -------- | ------ |
| What does this provision? | PostgreSQL users and databases on the **Platform RDS** |
| Is this for standalone or EKS-coupled RDS? | **Standalone** (bounded context per ADR-0158) |
| Does it create AWS RDS instances? | No - it creates objects **inside** an existing RDS |
| Does it use IRSA? | Only for Secrets Manager access, not for DB provisioning |
| Can multiple clusters use the same Platform RDS? | Yes, with proper networking |

---

## Part 1: The Mental Model

### What Is the Platform RDS?

The **Platform RDS** is a shared PostgreSQL instance that:

- Lives **independently** of any EKS cluster
- Survives cluster rebuilds and teardowns
- Hosts isolated databases for multiple applications (Keycloak, Backstage, app teams)
- Is managed as a "bounded context" - separate Terraform state, separate lifecycle

This is defined in [ADR-0158: Platform Standalone RDS Bounded Context](../../adrs/ADR-0158-platform-standalone-rds-bounded-context.md).

### Multi-Tenant Architecture

The Platform RDS is **multi-tenant** - a single PostgreSQL instance hosting isolated databases for multiple applications:

```text
┌─────────────────────────────────────────────────────────────────┐
│                    Platform RDS Instance                        │
│                 (goldenpath-platform-db-dev)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌───────────────┐  ┌───────────────┐  ┌───────────────┐       │
│   │   keycloak    │  │   backstage   │  │   myapp       │       │
│   │   (database)  │  │   (database)  │  │   (database)  │       │
│   │               │  │               │  │               │       │
│   │ keycloak_user │  │ backstage_user│  │ myapp_user    │       │
│   └───────────────┘  └───────────────┘  └───────────────┘       │
│                                                                 │
│   Each database is isolated:                                    │
│   - Own credentials (stored in Secrets Manager)                 │
│   - Own owner role (can't see other databases)                  │
│   - Own tables, schemas, data                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
         ▲                    ▲                    ▲
         │                    │                    │
    ┌────┴────┐          ┌────┴────┐          ┌────┴────┐
    │ Keycloak │          │Backstage│          │ Your App│
    │   Pod    │          │   Pod   │          │   Pod   │
    └──────────┘          └──────────┘          └──────────┘
```

**Why multi-tenant?**

| Benefit | Description |
| ------- | ----------- |
| **Cost** | One RDS instance (~$50-200/mo) vs many (~$50-200 each) |
| **Persistence** | Survives EKS cluster rebuilds (bounded context per ADR-0158) |
| **Simplicity** | One endpoint, one security group, one backup policy |
| **Isolation** | Each app has its own database + credentials (can't access others) |

### The Two-Step Gap

Terraform handles AWS resources, but PostgreSQL objects require SQL:

| Layer | What Terraform Does | What Provisioning Does |
| ----- | ------------------- | ---------------------- |
| AWS | Creates RDS instance | - |
| AWS | Creates Secrets Manager entries | - |
| PostgreSQL | - | Creates roles (users) |
| PostgreSQL | - | Creates databases |
| PostgreSQL | - | Grants privileges |

```text
BEFORE (Manual Gap):
  Terraform Apply → Secrets Created → [MANUAL psql] → DB Ready

AFTER (Automated):
  Terraform Apply → Secrets Created → rds-provision → DB Ready
```

### Prerequisites: What Must Exist First?

Before a user can request a database, the platform team must have provisioned:

| Prerequisite | Who Creates It | When | Lifecycle |
| ------------ | -------------- | ---- | --------- |
| VPC | Platform team | Once per environment | Persistent |
| Platform RDS instance | Platform team | Once per environment | Persistent |
| Master credentials | Terraform (RDS module) | When RDS is created | Persistent |
| EKS cluster | Platform team | As needed | Can be rebuilt |

**Key insight:** Users don't need their own VPC or cluster. They request a database on the **shared Platform RDS**.

---

## Part 2: The Provisioning Flow

### Backstage Form: What Users Fill Out

When a user requests a database via Backstage, they complete **one form** with these fields:

| Field | Required | Example | Description |
| ----- | -------- | ------- | ----------- |
| `database_name` | Yes | `inventory_service` | Name for the PostgreSQL database |
| `username` | Yes | `inventory_user` | PostgreSQL role that owns this database |
| `owner` | Yes | `app-team` | Team responsible for this database |
| `requester` | Yes | `daniel-deans` | Person submitting the request |
| `environment` | Yes | `dev` | Target environment (dev/staging/prod) |
| `domain` | Yes | `application` | Business domain classification |
| `risk` | Yes | `medium` | Data sensitivity (affects backup retention) |
| `initial_schema` | No | `none` | Optional pre-built schema template |

**Important:** Each form submission creates **one** database request. The provisioning script then processes **all** entries in tfvars but is **idempotent** - existing databases are skipped, only new ones are created.

### End-to-End Journey

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER JOURNEY                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. USER REQUEST (Backstage)                                            │
│     └── Fill 8-field form for ONE database request                      │
│              │                                                          │
│              ▼                                                          │
│  2. PR CREATED (GitHub Actions)                                         │
│     └── Updates tfvars + catalog, creates PR                            │
│              │                                                          │
│              ▼                                                          │
│  3. PR MERGED (Human approval)                                          │
│     └── Platform team reviews and merges to development                 │
│              │                                                          │
│              ▼                                                          │
│  4. AUTO-TRIGGERED (rds-database-apply.yml) ◄── AUTOMATED               │
│     └── Terraform apply (creates Secrets Manager entry)                 │
│     └── K8s Job runs provisioning in-cluster                            │
│     └── Creates PostgreSQL role + database + grants                     │
│              │                                                          │
│              ▼                                                          │
│  5. APP DEPLOYMENT                                                      │
│     └── ExternalSecret syncs credentials to K8s                         │
│     └── App connects to database                                        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### What Happens at Each Step

#### Step 1: Define Your Database

Add to `envs/<env>-rds/terraform.tfvars`:

```hcl
application_databases = {
  my_app = {
    database_name = "my_app"
    username      = "my_app_user"
  }
}
```

#### Step 2: Run Terraform

```bash
make rds-apply ENV=dev
```

**Creates:**
- Secret at `goldenpath/dev/my_app/postgres` containing username, password, host, port
- **Does NOT create** the PostgreSQL user or database

#### Step 3: Run Provisioning

```bash
# Preview first (safe, no changes)
make rds-provision-dry-run ENV=dev

# Then provision
make rds-provision ENV=dev
```

**Creates:**
- PostgreSQL role `my_app_user` with password from Secrets Manager
- PostgreSQL database `my_app` owned by that role
- Grants based on access level (owner/editor/reader)
- Audit record in `governance/<env>/rds_provision_audit.csv`

#### Step 4: App Connects

```yaml
# ExternalSecret syncs credentials to Kubernetes
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: my-app-db
spec:
  secretStoreRef:
    name: aws-secretsmanager
    kind: ClusterSecretStore
  data:
    - secretKey: POSTGRES_PASSWORD
      remoteRef:
        key: goldenpath/dev/my_app/postgres
        property: password
```

### Summary: Who Does What

| Step | Who | What Happens |
| ---- | --- | ------------ |
| 1 | User | Fills 8-field Backstage form for **one** database |
| 2 | Workflow | Creates PR adding entry to tfvars + catalog |
| 3 | Platform team | Reviews and merges PR to `development` |
| 4 | **Automated** | `rds-database-apply.yml` runs Terraform + K8s Job |
| 5 | K8s Job | Creates PostgreSQL role + database (idempotent) |
| 6 | App | Connects using credentials from Secrets Manager |

---

## Part 3: How the Script Works

### What It Does (and Does NOT Do)

| Does | Does NOT |
| ---- | -------- |
| Connects to PostgreSQL via psycopg2 | Create AWS resources |
| Runs SQL: CREATE ROLE, CREATE DATABASE, GRANT | Modify RDS instance settings |
| Fetches credentials from Secrets Manager | Use AWS RDS API |
| Writes audit records | Require IRSA for DB operations |

### Authentication Model

```text
┌──────────────────┐     ┌─────────────────────┐     ┌──────────────┐
│ Provisioning     │     │ AWS Secrets Manager │     │ Platform RDS │
│ Script           │     │                     │     │ (PostgreSQL) │
└────────┬─────────┘     └──────────┬──────────┘     └──────┬───────┘
         │                          │                       │
         │ 1. Fetch master secret   │                       │
         │ (boto3 - needs IAM/IRSA) │                       │
         │─────────────────────────>│                       │
         │<─────────────────────────│                       │
         │   {host, user, password} │                       │
         │                          │                       │
         │ 2. Fetch app secret      │                       │
         │─────────────────────────>│                       │
         │<─────────────────────────│                       │
         │   {password}             │                       │
         │                          │                       │
         │ 3. Connect via psycopg2 (SSL)                    │
         │─────────────────────────────────────────────────>│
         │                                                  │
         │ 4. CREATE ROLE, CREATE DATABASE, GRANT           │
         │─────────────────────────────────────────────────>│
         │<─────────────────────────────────────────────────│
         │   success                                        │
```

**IRSA is only needed for step 1-2** (Secrets Manager access via boto3). The actual database provisioning uses PostgreSQL credentials, not AWS IAM.

### Access Levels

| Level  | Use Case               | Database Grants  | Table Grants                   | Default Privileges |
| ------ | ---------------------- | ---------------- | ------------------------------ | ------------------ |
| owner  | Full control (default) | ALL PRIVILEGES   | ALL                            | ALL on future tables |
| editor | Read/write, no DDL     | CONNECT          | SELECT, INSERT, UPDATE, DELETE | Same on future tables |
| reader | Read-only access       | CONNECT          | SELECT                         | SELECT on future tables |

Example:

```hcl
application_databases = {
  analytics_readonly = {
    database_name = "analytics"
    username      = "analytics_reader"
    access_level  = "reader"
  }
}
```

---

## Part 4: Federation and Multi-Cluster Access

### Can Multiple Clusters Share the Platform RDS?

**Yes.** The Platform RDS can serve databases to any workload with network access.

### Current Setup (Single VPC)

```text
┌─────────────────────────────────────────────────────┐
│                    VPC (dev)                        │
│                                                     │
│   ┌─────────────┐        ┌─────────────┐            │
│   │   EKS       │        │  Platform   │            │
│   │   Cluster   │───────>│  RDS        │            │
│   │             │        │             │            │
│   │ - Backstage │        │ - keycloak  │            │
│   │ - Keycloak  │        │ - backstage │            │
│   │ - Apps      │        │ - app DBs   │            │
│   └─────────────┘        └─────────────┘            │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Federation Pattern: VPC Peering

Connect clusters in different VPCs to the same Platform RDS:

```text
┌─────────────────────┐           ┌─────────────────────┐
│    VPC-A (Platform) │           │    VPC-B (Team)     │
│                     │           │                     │
│   ┌─────────────┐   │   peering │   ┌─────────────┐   │
│   │  Platform   │<──┼───────────┼───│  Team EKS   │   │
│   │  RDS        │   │           │   │  Cluster    │   │
│   └─────────────┘   │           │   └─────────────┘   │
│                     │           │                     │
└─────────────────────┘           └─────────────────────┘
```

**Requirements:**
- VPC peering or Transit Gateway between VPCs
- Security group rules allowing remote CIDR on port 5432
- DNS resolution (Route53 private hosted zone or use IP)

### Federation Pattern: PrivateLink

For cross-account access without VPC peering:

```text
┌─────────────────────┐           ┌─────────────────────┐
│   Account A         │           │   Account B         │
│                     │           │                     │
│   ┌─────────────┐   │           │   ┌─────────────┐   │
│   │  Platform   │   │           │   │  Consumer   │   │
│   │  RDS        │   │           │   │  Cluster    │   │
│   └──────┬──────┘   │           │   └──────┬──────┘   │
│          │          │           │          │          │
│   ┌──────▼──────┐   │           │   ┌──────▼──────┐   │
│   │  Endpoint   │───┼───────────┼───│   VPC       │   │
│   │  Service    │   │PrivateLink│   │   Endpoint  │   │
│   └─────────────┘   │           │   └─────────────┘   │
│                     │           │                     │
└─────────────────────┘           └─────────────────────┘
```

### What the Provisioning Script Doesn't Care About

The script only needs:
1. Network path to RDS (however you achieve it)
2. Credentials from Secrets Manager
3. The tfvars file

It doesn't know or care whether the connection comes from:
- Same VPC
- Peered VPC
- PrivateLink
- VPN
- Bastion host

---

## Part 5: Operational Details

### Idempotency

The script is **safe to re-run**:

| Scenario               | Behavior                         |
| ---------------------- | -------------------------------- |
| Role doesn't exist     | Creates role                     |
| Role exists            | Updates password (no error)      |
| Database doesn't exist | Creates database                 |
| Database exists        | Skips (logs "no_change")         |
| Run twice              | Second run shows all "no_change" |

### Approval Gates

| Environment | Approval Required |
| ----------- | ----------------- |
| dev | No |
| test | Yes (`ALLOW_DB_PROVISION=true`) |
| staging | Yes |
| prod | Yes |

```bash
# Dev - no approval
make rds-provision ENV=dev

# Prod - requires explicit approval
ALLOW_DB_PROVISION=true make rds-provision ENV=prod
```

### Error Handling (Fail-Fast)

By default, the script exits on first error:

| Error Type           | Behavior                     |
| -------------------- | ---------------------------- |
| Secret not found     | Exits immediately with error |
| Connection timeout   | Exits immediately with error |
| Permission denied    | Exits immediately with error |
| Database wrong owner | Logs warning, continues      |

To continue on errors (not recommended for prod):

```bash
python3 scripts/rds_provision.py --env dev --no-fail-fast ...
```

### Audit Trail

Every run produces CSV audit records:

```csv
timestamp_utc,environment,build_id,run_id,database,username,action,status,duration_ms,message
2026-01-16T10:30:00Z,dev,manual,local,my_app,my_app_user,create_role,success,45,Created role
2026-01-16T10:30:00Z,dev,manual,local,my_app,my_app_user,create_database,success,120,Created database
```

Persisted to: `governance/<env>/rds_provision_audit.csv`

---

## Part 6: Common Questions

### Q: Does the user need their own VPC or cluster?

**No.** Users request a database on the shared Platform RDS. They only need their app to have network access to reach it (which the platform provides).

### Q: Is this for the standalone RDS or the EKS-coupled build?

**Standalone.** The `envs/<env>-rds/` directory is for the persistent Platform RDS that survives cluster rebuilds. This is per ADR-0158.

### Q: Does provisioning use IRSA to assume a role?

**Partially.** IRSA is used for boto3 to fetch secrets from Secrets Manager. The actual PostgreSQL provisioning uses database credentials (master user), not AWS IAM.

### Q: Can the Platform RDS serve databases to other clusters?

**Yes.** With proper networking (VPC peering, Transit Gateway, or PrivateLink), any cluster can connect to the Platform RDS. The provisioning script creates the database; networking determines who can reach it.

### Q: Do I need a new workflow for provisioning?

**No.** The provisioning is now automated. When a PR is merged to `development` that modifies `envs/*-rds/terraform.tfvars`, the `rds-database-apply.yml` workflow triggers automatically. It:

1. Runs Terraform apply to create/update secrets
2. Creates a K8s Job in the cluster to run provisioning (has VPC access via IRSA)

### Q: What if the RDS doesn't exist yet?

The Platform RDS must be created first by the platform team via `make rds-apply`. Once it exists, users can request databases on it.

---

## Part 7: Automation Architecture

### Current Implementation (V1.1)

The provisioning is now fully automated via GitHub Actions + K8s Job:

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                      AUTOMATED PROVISIONING FLOW                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. PR MERGED TO development                                            │
│     └── Triggers: rds-database-apply.yml                                │
│              │                                                          │
│              ▼                                                          │
│  2. DETECT ENVIRONMENT                                                  │
│     └── Parses changed files: envs/*-rds/terraform.tfvars               │
│              │                                                          │
│              ▼                                                          │
│  3. TERRAFORM APPLY                                                     │
│     └── Creates/updates secrets in AWS Secrets Manager                  │
│              │                                                          │
│              ▼                                                          │
│  4. K8S JOB CREATED                                                     │
│     └── Job: rds-provision-{env}-{run_number}                           │
│     └── Namespace: platform-system                                      │
│     └── ServiceAccount: platform-provisioner (IRSA)                     │
│              │                                                          │
│              ▼                                                          │
│  5. PROVISIONING RUNS IN-CLUSTER                                        │
│     └── Has VPC access to RDS endpoint                                  │
│     └── Fetches secrets via IRSA → Secrets Manager                      │
│     └── Creates PostgreSQL roles + databases                            │
│              │                                                          │
│              ▼                                                          │
│  6. JOB COMPLETES                                                       │
│     └── Logs captured in GitHub Actions                                 │
│     └── Audit CSV written to /tmp/audit.csv                             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key Components

| Component | Location | Purpose |
| --------- | -------- | ------- |
| Auto-apply workflow | `.github/workflows/rds-database-apply.yml` | Triggers on merge |
| ServiceAccount + RBAC | `gitops/kustomize/platform-system/rds-provisioner-rbac.yaml` | IRSA for Secrets Manager |
| Argo WorkflowTemplate | `gitops/kustomize/platform-system/rds-provision-workflowtemplate.yaml` | Alternative to inline Job |
| Namespace | `gitops/kustomize/bases/namespaces.yaml` | `platform-system` |

### Manual Fallback

If automation fails, platform engineers can still run manually:

```bash
# Dry run first
make rds-provision-dry-run ENV=dev

# Then provision
make rds-provision ENV=dev
```

Or via Argo WorkflowTemplate:

```bash
argo submit --from workflowtemplate/rds-provision \
  -n platform-system \
  -p environment=dev \
  -p build_id=manual \
  -p dry_run=false
```

### Future Improvements (V2)

| Improvement | Benefit | Status |
| ----------- | ------- | ------ |
| K8s Job-based provisioning | Runs in VPC, fully automated | **Implemented** |
| CI workflow integration | Fully automated post-apply | **Implemented** |
| Argo WorkflowTemplate | Alternative trigger, UI visibility | **Implemented** |
| Delegated admin role | Least-privilege, not master creds | Deferred |
| Cross-region replication | DR and read replicas | Not planned |

---

## Related Documentation

- [RDS Request Flow](./RDS_REQUEST_FLOW.md) - How to request a new database via Backstage
- [ADR-0158: Standalone RDS Bounded Context](../../adrs/ADR-0158-platform-standalone-rds-bounded-context.md) - Why Platform RDS is standalone
- [ADR-0165: Automated Provisioning](../../adrs/ADR-0165-rds-user-db-provisioning-automation.md) - Design decision for this script
- [PRD-0001: RDS Provisioning](../../20-contracts/prds/PRD-0001-rds-user-db-provisioning.md) - Requirements
- [RB-0032: Provisioning Runbook](../../70-operations/runbooks/RB-0032-rds-user-provision.md) - Operations guide
- [Platform RDS Architecture](../../70-operations/30_PLATFORM_RDS_ARCHITECTURE.md) - Infrastructure details
