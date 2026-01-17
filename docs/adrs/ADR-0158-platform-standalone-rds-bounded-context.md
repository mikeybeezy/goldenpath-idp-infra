---
id: ADR-0158-platform-standalone-rds-bounded-context
title: 'ADR-0158: Standalone RDS as Bounded Context with Deletion Protection'
type: adr
status: accepted
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: manual-console-only
  observability_tier: gold
schema_version: 1
relates_to:
  - 30_PLATFORM_RDS_ARCHITECTURE
  - ADR-0006
  - ADR-0007
  - ADR-0053
  - ADR-0157
  - ADR-0158
  - ADR-0165
  - ADR-0165-rds-user-db-provisioning-automation
  - ADR-0166
  - ADR-0166-rds-dual-mode-automation-and-enum-alignment
  - PRD-0001-rds-user-db-provisioning
  - RDS_DUAL_MODE_AUTOMATION
  - RDS_REQUEST_FLOW
  - RDS_USER_DB_PROVISIONING
supersedes:
  - ADR-0157
superseded_by: []
tags:
  - rds
  - database
  - bounded-context
  - persistence
  - deletion-protection
inheritance: {}
value_quantification:
  vq_class: 🟢 HV/HQ
  impact_tier: high
  potential_savings_hours: 80.0
supported_until: 2028-01-15
version: 1.0
breaking_change: true
---
## ADR-0158: Standalone RDS as Bounded Context with Deletion Protection

- **Status:** Accepted
- **Date:** 2026-01-15
- **Owners:** Platform Team
- **Domain:** Platform
- **Decision type:** Architecture / Operations / Security
- **Related:** ADR-0006 (Secrets Strategy), ADR-0157 (Multi-Tenant RDS - superseded)
- **Supersedes:** ADR-0157

---

## Context

ADR-0157 established multi-tenant RDS for platform tooling but coupled it to the EKS cluster Terraform state. This creates problems:

1. **Ephemeral cluster rebuilds risk data loss** - RDS tied to cluster lifecycle
2. **Accidental deletion** - `terraform destroy` on cluster could destroy database
3. **Tight coupling** - Users cannot spin up vanilla clusters without RDS
4. **Blast radius** - Single state file controls both compute and data

Our platform philosophy emphasizes **bounded contexts** with clear separation of concerns. The data layer (RDS) and compute layer (EKS) have fundamentally different lifecycles:

|Layer|Lifecycle|Rebuild Frequency|Data Sensitivity|
|-------|-----------|-------------------|------------------|
|EKS Cluster|Ephemeral|Weekly/Daily|None (stateless)|
|RDS Database|Persistent|Never (ideally)|High (stateful)|

---

## Decision

We will extract Platform RDS into a **standalone Terraform root** with its own state, making it a prerequisite bolt-on that persists across all cluster rebuilds.

### Core Principles

1. **Bounded Context** - RDS has its own Terraform root, state, and lifecycle
2. **Persistence by Default** - RDS is never suffixed with build_id, never ephemeral
3. **Deletion Protection** - Intentionally difficult to delete; requires console intervention
4. **Deploy First** - Must be deployed before any cluster that depends on it
5. **Region Agnostic** - Configuration supports any AWS region
6. **Optional Bolt-On** - Clusters can run without RDS (using bundled PostgreSQL)

### Architecture

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    BOUNDED CONTEXT SEPARATION                                │
└─────────────────────────────────────────────────────────────────────────────┘

  DATA LAYER (Persistent)                    COMPUTE LAYER (Ephemeral)
  ───────────────────────                    ────────────────────────

  envs/dev-rds/                              envs/dev/
  ├── main.tf                                ├── main.tf
  ├── variables.tf                           ├── variables.tf
  └── terraform.tfvars                       └── terraform.tfvars

  State: s3://.../envs/dev-rds/tfstate       State: s3://.../envs/dev/builds/{id}/tfstate

  Lifecycle: PERSISTENT                      Lifecycle: EPHEMERAL
  Deletion: CONSOLE ONLY                     Deletion: terraform destroy

  ┌─────────────────────────┐                ┌─────────────────────────┐
  │   Platform RDS          │                │   EKS Cluster           │
  │   goldenpath-platform-db│                │   (build-15-01-26-01)   │
  │                         │                │                         │
  │   Databases:            │◄───────────────│   Apps:                 │
  │   - keycloak            │   Secrets      │   - Keycloak            │
  │   - backstage           │   via ESO      │   - Backstage           │
  └─────────────────────────┘                └─────────────────────────┘
```

### Deletion Protection Strategy

RDS deletion is **intentionally difficult** via multiple layers:

|Protection Layer|Mechanism|Bypass Method|
|------------------|-----------|---------------|
|Terraform `deletion_protection`|RDS API refuses delete|Console disable required|
|Terraform `prevent_destroy`|Lifecycle meta-argument|Manual state removal|
|S3 State Lock|DynamoDB locking|Manual unlock|
|No CI Destroy Workflow|No automated teardown|Manual only|
|AWS Console MFA|IAM policy|Physical MFA required|

### To delete RDS, an operator must

1. Log into AWS Console (not CLI/Terraform)
2. Disable deletion protection on RDS instance
3. Confirm deletion with MFA
4. Manually remove from Terraform state (if needed)

This is intentional friction to prevent accidental data loss.

### Deployment Sequence

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DEPLOYMENT ORDER                                     │
└─────────────────────────────────────────────────────────────────────────────┘

  STEP 1: Platform RDS (One-Time or Rare)
  ───────────────────────────────────────

  cd envs/dev-rds
  terraform init
  terraform apply

  Creates:
  ├── RDS Instance (goldenpath-platform-db)
  ├── DB Subnet Group
  ├── Security Group (VPC CIDR access)
  ├── Parameter Group
  └── Secrets in AWS Secrets Manager
      ├── goldenpath/{env}/rds/master
      ├── goldenpath/{env}/keycloak/postgres
      └── goldenpath/{env}/backstage/postgres

  ─────────────────────────────────────────────────────────────────────────────

  STEP 2: EKS Cluster (Ephemeral, Repeatable)
  ───────────────────────────────────────────

  cd envs/dev
  terraform apply -var="build_id=15-01-26-01"
  make bootstrap

  Creates:
  ├── VPC, Subnets, NAT Gateway
  ├── EKS Cluster + Node Groups
  ├── IAM Roles (IRSA)
  └── Kubernetes Resources
      ├── External Secrets Operator
      ├── ClusterSecretStore
      └── ExternalSecrets (sync from Secrets Manager)

  ─────────────────────────────────────────────────────────────────────────────

  STEP 3: Platform Apps (Via ArgoCD)
  ──────────────────────────────────

  ArgoCD syncs:
  ├── Keycloak (connects to RDS via ExternalSecret)
  ├── Backstage (connects to RDS via ExternalSecret)
  └── Other tooling apps
```

### Trade-Off: Deploy RDS First

### The price of persistence is deployment order

Users who want platform apps with external RDS must deploy RDS first. This is an acceptable trade-off because:

1. RDS is deployed once, clusters are deployed many times
2. Clear dependency makes the architecture understandable
3. Users who don't need RDS can skip it (use bundled PostgreSQL)
4. Prevents the "works on my machine" problem with missing dependencies

---

## Scope

### Applies To

- Platform RDS for tooling apps (Keycloak, Backstage)
- All environments: dev, staging, prod
- Any AWS region (region-agnostic configuration)

### Does Not Apply To

- Application workload databases (tenant responsibility)
- Local development (uses bundled PostgreSQL)
- Ephemeral test databases (use bundled)

---

## Consequences

### Positive

- **Data survives cluster teardowns** - Database persists independently
- **Clear ownership boundary** - Separate state, separate concerns
- **Reduced blast radius** - Cluster destroy cannot touch RDS
- **Intentional deletion friction** - Protects against accidents
- **Vanilla clusters remain possible** - RDS is optional
- **Region agnostic** - Deploy to any region via variables

### Tradeoffs / Risks

- **Deployment order matters** - RDS must exist before apps need it
- **Two terraform applies** - Slightly more operational steps
- **Orphaned RDS possible** - If all clusters deleted, RDS remains (by design)
- **Cross-state references** - Apps must discover RDS via Secrets Manager, not Terraform outputs

### Mitigations

- Document deployment order clearly
- Makefile targets for combined workflows
- Secrets Manager as the integration point (no direct Terraform references)
- Cost monitoring for orphaned RDS instances

---

## Alternatives Considered

### 1. Keep RDS in Cluster State (ADR-0157)

- **Rejected** - Couples ephemeral compute to persistent data
- Risk of accidental deletion during cluster teardown

### 2. Terraform Workspaces

- **Rejected** - Workspaces share the same root, not true separation
- Confusing mental model for operators

### 3. Terraform `-target` for Partial Applies

- **Rejected** - Fragile, not a real boundary
- State still contains both resources

### 4. Separate AWS Account for Data Layer

- **Considered for future** - Maximum isolation
- Overkill for current scale, adds cross-account complexity

---

## Implementation

### Directory Structure

```text
envs/
├── dev/                          # EKS cluster (ephemeral)
│   ├── main.tf
│   ├── variables.tf
│   └── terraform.tfvars
│
├── dev-rds/                      # Platform RDS (persistent) ◄── NEW
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── terraform.tfvars
│
├── staging/
├── staging-rds/
├── prod/
└── prod-rds/
```

### State Keys

|Environment|Resource|State Key|
|-------------|----------|-----------|
|dev|RDS|`envs/dev-rds/terraform.tfstate`|
|dev|Cluster (persistent)|`envs/dev/terraform.tfstate`|
|dev|Cluster (ephemeral)|`envs/dev/builds/{build_id}/terraform.tfstate`|
|staging|RDS|`envs/staging-rds/terraform.tfstate`|
|prod|RDS|`envs/prod-rds/terraform.tfstate`|

### Makefile Targets

```makefile
# RDS targets (persistent layer)
rds-init:
    terraform -chdir=envs/$(ENV)-rds init

rds-plan:
    terraform -chdir=envs/$(ENV)-rds plan

rds-apply:
    terraform -chdir=envs/$(ENV)-rds apply

# No rds-destroy target - intentional!
# Deletion requires console intervention

# Combined workflow
platform-up: rds-apply apply bootstrap
    @echo "Platform deployed: RDS + Cluster + Bootstrap"
```

### Region Configuration

```hcl
# envs/dev-rds/variables.tf
variable "aws_region" {
  type        = string
  description = "AWS region for RDS deployment"
  # No default - must be explicitly set per environment
}

# envs/dev-rds/terraform.tfvars
aws_region = "eu-west-2"  # London
# aws_region = "us-east-1"  # Virginia
# aws_region = "ap-southeast-1"  # Singapore
```

---

## V1 Scope

### V1 Must Have

|Feature|Description|Status|
|---------|-------------|--------|
|Separate Terraform root|`envs/{env}-rds/` with own state|Planned|
|Deletion protection|`deletion_protection = true`|Planned|
|Prevent destroy lifecycle|Terraform refuses to destroy|Planned|
|Automated snapshots|7 days (dev), 35 days (prod)|Planned|
|CloudWatch alarms|CPU, memory, storage, connections|Planned|
|Encryption at rest|KMS-managed key|Planned|
|SSL/TLS required|`rds.force_ssl` parameter|Planned|
|Makefile targets|`rds-init`, `rds-plan`, `rds-apply` (no destroy)|Planned|
|Deployment documentation|Sequence, runbooks|Planned|
|Performance Insights|Query analysis enabled|Planned|
|Operational runbooks|Backup, restore, rotation, scaling|Planned|
|Cost tags|`CostCenter`, `Environment`, `Application`|Planned|
|Password rotation documentation|Manual procedure documented|Planned|
|Automated secret rotation|AWS Secrets Manager Lambda rotation|Planned|

### V2 Future Enhancements

|Feature|Description|Rationale for Deferral|
|---------|-------------|------------------------|
|Cross-region snapshot copy|DR to secondary region|Adds complexity, evaluate after prod usage|
|PgBouncer connection pooling|Connection multiplexing|Only needed at scale|
|Read replicas|Offload read queries|Only if Backstage catalog queries become heavy|
|IAM database authentication|Token-based auth|Current secret-based auth is sufficient|
|Separate AWS account|Maximum isolation|Overkill for current scale|

---

## Monitoring & Alerting (V1)

### CloudWatch Alarms

|Metric|Warning Threshold|Critical Threshold|Action|
|--------|-------------------|---------------------|--------|
|CPUUtilization|> 70% for 5min|> 90% for 5min|Scale up instance|
|FreeableMemory|< 512MB|< 256MB|Scale up instance|
|FreeStorageSpace|< 30%|< 15%|Increase storage|
|DatabaseConnections|> 70% of max|> 90% of max|Check for leaks, add pooling|
|ReadLatency|> 50ms|> 100ms|Check queries, add read replica|
|WriteLatency|> 50ms|> 100ms|Check queries, scale IOPS|

### Performance Insights

Enabled by default for query analysis:

- Top SQL by wait time
- Database load by wait type
- Slice-and-dice by application

---

## Security Configuration (V1)

### Encryption

```hcl
# At-rest encryption (KMS)
storage_encrypted = true
kms_key_id        = aws_kms_key.rds.arn  # Or use default aws/rds

# In-transit encryption (SSL required)
parameter {
  name  = "rds.force_ssl"
  value = "1"
}
```

### Network Security

```hcl
# Security group allows only VPC CIDR
ingress {
  from_port   = 5432
  to_port     = 5432
  protocol    = "tcp"
  cidr_blocks = [var.vpc_cidr]  # e.g., 10.0.0.0/16
  description = "PostgreSQL from VPC"
}

# No public access
publicly_accessible = false
```

---

## Secret Rotation (V1)

### Secret Rotation Architecture

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AUTOMATED SECRET ROTATION                                 │
└─────────────────────────────────────────────────────────────────────────────┘

  AWS Secrets Manager                    Lambda Rotation Function
  ─────────────────────                  ────────────────────────

  ┌─────────────────────────┐            ┌─────────────────────────┐
  │ goldenpath/dev/keycloak │            │ SecretsManagerRDS       │
  │ /postgres               │◄──────────▶│ PostgreSQLSingleUser    │
  │                         │  Triggers  │ Rotation Lambda         │
  │ rotation_enabled: true  │            │                         │
  │ rotation_days: 30       │            │ 1. Create new password  │
  └─────────────────────────┘            │ 2. Set in RDS           │
                                         │ 3. Test connection      │
                                         │ 4. Update secret        │
                                         └─────────────────────────┘
                                                    │
                                                    ▼
                                         ┌─────────────────────────┐
                                         │ RDS PostgreSQL          │
                                         │ ALTER USER ... PASSWORD │
                                         └─────────────────────────┘
```

### Rotation Schedule

|Environment|Rotation Period|Rationale|
|-------------|-----------------|-----------|
|dev|30 days|Balance security with operational overhead|
|staging|30 days|Match dev for consistency|
|prod|14 days|Higher security posture|

### ESO Refresh

ExternalSecrets `refreshInterval: 1h` ensures K8s secrets update within 1 hour of rotation.
Apps using connection pools may need pod restart to pick up new credentials.

---

## Operational Runbooks (V1)

### RB-0012: RDS Backup and Restore

**Purpose:** Restore database from automated snapshot or point-in-time recovery.

### Steps (RB-0012: RDS Backup and Restore)

1. Identify target snapshot or PITR timestamp
2. Create new RDS instance from snapshot
3. Update Secrets Manager with new endpoint
4. Verify app connectivity
5. (Optional) Promote new instance, decommission old

### RB-0013: RDS Password Rotation (Manual)

**Purpose:** Rotate application database passwords manually.

### Steps (RB-0013: RDS Password Rotation (Manual))

1. Generate new 32-character password
2. Update AWS Secrets Manager secret
3. Force ESO refresh: `kubectl annotate externalsecret ... force-sync=$(date +%s)`
4. Restart app pods to pick up new credentials
5. Verify connectivity

### RB-0014: RDS Multi-AZ Failover

**Purpose:** Handle Multi-AZ failover events.

**Automatic:** AWS handles failover automatically (~60-120s)

### Manual verification

1. Check RDS events in console
2. Verify new primary endpoint
3. Confirm app reconnection
4. Review CloudWatch metrics

### RB-0015: RDS Scaling

**Purpose:** Vertically scale RDS instance class.

### Steps (RB-0015: RDS Scaling)

1. Schedule maintenance window (if not apply_immediately)
2. Modify instance class via console or Terraform
3. Monitor failover during modification
4. Verify app connectivity post-scale
5. Update Terraform state to match

### RB-0016: RDS Deletion (Break-Glass)

**Purpose:** Permanently delete RDS instance (irreversible).

### Prerequisites

- Explicit approval from platform lead
- Final snapshot taken and verified
- All dependent apps migrated or decommissioned

### Steps (RB-0016: RDS Deletion (Break-Glass))

1. Log into AWS Console (not CLI)
2. Navigate to RDS > Databases
3. Select instance, click Modify
4. Disable deletion protection, Apply immediately
5. Select instance, click Delete
6. Confirm by typing instance name
7. Choose whether to create final snapshot
8. Remove from Terraform state: `terraform state rm module.platform_rds`

---

## Follow-ups

### V1 Implementation

- [ ] Create `envs/dev-rds/` Terraform root
- [ ] Remove RDS from `envs/dev/main.tf`
- [ ] Add Makefile targets for RDS operations
- [ ] Add CloudWatch alarms module
- [ ] Configure SSL/TLS requirement
- [ ] Enable Performance Insights
- [ ] Configure automated secret rotation (Lambda)
- [ ] Add cost tags to all resources
- [ ] Create operational runbooks (RB-0012 through RB-0016)
- [ ] Update deployment documentation
- [ ] Update 30_PLATFORM_RDS_ARCHITECTURE.md
- [ ] Update 35_TOOLING_SECRETS_LIFECYCLE.md

### V1.1/V2 Backlog

- [ ] Cross-region snapshot copy for DR
- [ ] PgBouncer connection pooling
- [ ] Read replicas for heavy read workloads
- [ ] IAM database authentication
- [ ] Separate AWS account for data layer

---

## Notes

- ADR-0157 is superseded but remains as historical record
- RDS credentials flow: Terraform → Secrets Manager → ESO → K8s Secrets → Apps
- For local development, apps use bundled PostgreSQL (no RDS dependency)
- Consider Aurora Serverless v2 for production if usage patterns warrant it
- The "deploy RDS first" requirement is the **intentional trade-off** for data persistence
- Secret rotation uses AWS-managed Lambda; apps must handle connection refresh
