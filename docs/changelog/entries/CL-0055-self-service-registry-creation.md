---
id: CL-0055-self-service-registry-creation
title: 'CL-0055: Self-Service ECR Registry Creation Workflow'
type: changelog
category: governance
version: '1.0'
owner: platform-team
status: active
dependencies:
  - github-actions
  - yq
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
lifecycle:
  supported_until: 2027-01-05
  breaking_change: false
relates_to:
  - ADR-0095
  - ADR-0092
  - CL-0055
---

# CL-0055: Self-Service ECR Registry Creation Workflow

**Date:** 2026-01-05  
**Type:** Feature  
**Category:** Governance  
**Status:** Active

## Summary

Created GitHub Actions workflow for self-service ECR registry creation requests.

## Changes

### New Files
- `.github/workflows/create-ecr-registry.yml` - Registry creation workflow
- `docs/adrs/ADR-0095-self-service-registry-creation.md` - Decision record

### Workflow Features

**Trigger:** Manual (workflow_dispatch)

**Inputs:**
- `registry_name`: Registry name (lowercase-with-hyphens)
- `owner`: Team owner (app-team-name)
- `risk`: Risk level (low/medium/high)
- `id`: Registry ID (REGISTRY_UPPERCASE)
- `environment`: Target environment (dev/test/staging/prod)

**Process:**
1. Validates all inputs against naming conventions
2. Updates `docs/registry-catalog.yaml` (idempotent)
3. Updates `envs/{env}/terraform.tfvars` (idempotent)
4. Creates PR with all changes
5. Platform team reviews and merges
6. Terraform apply provisions registry

**Validation:**
- Registry name: `^[a-z][a-z0-9-]*$`
- Owner: `^app-team-[a-z0-9-]+$`
- ID: `^REGISTRY_[A-Z0-9_]+$`

## Impact

### Platform Team
- Reduced manual toil (no file editing)
- Automated validation (fewer errors)
- PR-based workflow (audit trail)

### Application Teams
- Self-service registry requests
- No Terraform knowledge required
- Clear validation errors
- Faster turnaround (no back-and-forth)

## Implementation Status

- ✅ Workflow created
- ✅ ADR documented
- ✅ Validation rules implemented
- ⏳ User documentation (pending)

## Next Steps

1. Add workflow to GitHub Actions index
2. Create user guide for app teams
3. Test workflow with sample registry
4. Announce to app teams

## Testing

- [ ] Workflow triggers successfully
- [ ] Input validation works
- [ ] Catalog updates correctly
- [ ] Tfvars updates correctly
- [ ] PR created with correct content
- [ ] Idempotent (safe to re-run)

## Related
- [ADR-0095: Self-Service Registry Creation](../adrs/ADR-0095-self-service-registry-creation.md)
- [ADR-0092: ECR Registry Product Strategy](../adrs/ADR-0092-ecr-registry-product-strategy.md)

