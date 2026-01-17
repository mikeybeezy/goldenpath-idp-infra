---
id: CL-0130
title: RDS Optional Toggle Integration
type: changelog
status: active
date: 2026-01-15
adr_ref: ADR-0160
domain: platform-core
owner: platform-team
lifecycle: active
schema_version: 1
tags:
  - rds
  - infrastructure
  - self-service
relates_to:
  - ADR-0158
  - ADR-0160
---
## Summary

Added optional RDS toggle to EKS environment configuration, providing a second deployment model alongside the existing standalone bounded context (ADR-0158).

## Changes

### Added

- `module "platform_rds"` in `envs/dev/main.tf` with conditional creation
- Enhanced `rds_config` variable with full configuration options
- RDS outputs for connection details and secret ARNs

### Modified

- `envs/dev/terraform.tfvars`: `rds_config` available with `enabled` toggle
- `envs/dev/variables.tf`: Enhanced `rds_config` type definition

### Unchanged

- `envs/dev-rds/` directory (standalone option, wired to Backstage)

## Two Deployment Models

|Model|Command|Use Case|
|---|---|---|
|Standalone (A)|`make rds-apply` then `make apply`|RDS survives cluster teardown|
|Coupled (B)|`make apply` with `enabled = true`|Single-command deployment|

## Configuration (Coupled Option)

```hcl
rds_config = {
  enabled               = true   # Toggle on/off
  identifier            = "goldenpath-platform-db"
  instance_class        = "db.t3.micro"
  application_databases = {
    keycloak  = { database_name = "keycloak", username = "keycloak" }
    backstage = { database_name = "backstage", username = "backstage" }
  }
}
```

## Related

- ADR-0160: RDS Optional Toggle Integration
- ADR-0158: Platform Standalone RDS Bounded Context (unchanged)
