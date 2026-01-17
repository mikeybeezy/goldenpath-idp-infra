---
id: ADR-0160
title: RDS Optional Toggle Integration
type: adr
status: accepted
date: 2026-01-15
deciders:
  - platform-team
extends:
  - ADR-0158
domain: platform-core
owner: platform-team
lifecycle: active
schema_version: 1
tags:
  - rds
  - infrastructure
  - self-service
relates_to:
  - 01_adr_index
  - ADR-0157-platform-multi-tenant-rds-architecture
  - ADR-0158-platform-standalone-rds-bounded-context
  - ADR-0160
  - ADR-0166
  - CL-0130
  - CL-0133-idp-stack-deployment-runbook
  - RB-0030-rds-break-glass-deletion
  - RB-0031-idp-stack-deployment
  - RDS_DUAL_MODE_AUTOMATION
---
## Status

Accepted

## Context

ADR-0158 introduced RDS as a standalone bounded context (`envs/dev-rds/`) to ensure data persistence across cluster rebuilds. This works well for users who need decoupled lifecycle management and is already wired to Backstage self-service.

However, some users have simpler needs:

1. **Single-Command Deployment**: Deploy cluster with RDS in one `make apply`
2. **Add RDS Later**: Start without RDS, enable it later via toggle
3. **Simpler Mental Model**: One state file, one environment directory

Both use cases are valid. Rather than choosing one approach, we support both.

## Decision

Support two deployment models for Platform RDS:

### Option A: Standalone RDS (Existing - ADR-0158)

Decoupled bounded context for users who need independent lifecycle management.

- **Directory**: `envs/dev-rds/`
- **Command**: `make rds-apply ENV=dev` (separate from EKS)
- **Backstage**: Already wired to self-service templates
- **Use case**: Platform team, users needing RDS to survive cluster rebuilds

### Option B: Coupled RDS (New)

Toggle in EKS config for users who want single-command deployment.

```hcl
rds_config = {
  enabled               = true   # Toggle on/off
  identifier            = "goldenpath-platform-db"
  instance_class        = "db.t3.micro"
  engine_version        = "15.4"
  allocated_storage     = 20
  max_allocated_storage = 50
  multi_az              = false
  deletion_protection   = true
  skip_final_snapshot   = false
  backup_retention_days = 7
  application_databases = {
    keycloak = {
      database_name = "keycloak"
      username      = "keycloak"
    }
    backstage = {
      database_name = "backstage"
      username      = "backstage"
    }
  }
}
```

The existing `modules/aws_rds/` module is called conditionally:

```hcl
module "platform_rds" {
  source = "../../modules/aws_rds"
  count  = var.rds_config.enabled ? 1 : 0
  # ...
}
```

## When to Use Which

|Requirement|Use Standalone (A)|Use Coupled (B)|
|---|---|---|
|RDS must survive cluster teardown|Yes|No|
|Single-command deployment|No|Yes|
|Backstage self-service|Yes (wired)|Future|
|Independent state management|Yes|No|
|Simpler mental model|No|Yes|

## User Journey (Coupled Option)

|Day|User Need|Action|
|---|---|---|
|1|Just need a cluster|`enabled = false`, run `make apply`|
|30|Now I need a database|Change to `enabled = true`, run `make apply`|
|60|Add another app database|Add to `application_databases`, run `make apply`|

## Consequences

### Positive

- **Choice**: Users pick the model that fits their needs
- **Backwards Compatible**: Standalone option remains fully functional
- **Self-Service Ready**: Standalone already wired to Backstage
- **Simple Path**: Coupled option for users who want single-command

### Negative

- **Two Patterns**: Users must understand when to use which
- **Documentation**: Need clear guidance on choosing

### Mitigations

- Clear decision matrix in docs
- Default to standalone for platform deployments
- Coupled option defaults to `enabled = false`

## Related

- ADR-0158: Platform Standalone RDS Bounded Context (extended, not superseded)
- ADR-0157: Platform Multi-Tenant RDS Architecture
- RB-0030: RDS Break-Glass Deletion Procedure
