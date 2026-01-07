---
id: ADR-0095-self-service-registry-creation
title: 'ADR-0095: Self-Service ECR Registry Creation Workflow'
type: adr
status: active
lifecycle: active
version: '1.0'
supported_until: '2028-01-01'
breaking_change: false
---

# ADR-0095: Self-Service ECR Registry Creation Workflow

## Status
Accepted

## Context

Application teams need to request ECR registries, but the current process requires manual file editing and Terraform knowledge. This creates friction and bottlenecks the platform team.

## Decision

Create a GitHub Actions workflow (`create-ecr-registry.yml`) that provides a self-service interface for registry creation requests.

### How It Works

1. **App team** triggers workflow via GitHub UI
2. **Inputs:** registry name, owner, risk, ID, environment
3. **Validation:** Enforces naming conventions and metadata format
4. **Updates:**
   - Adds entry to `docs/registry-catalog.yaml`
   - Adds entry to `envs/{env}/terraform.tfvars`
5. **Creates PR** with all changes for platform team review
6. **Platform team** reviews and merges
7. **Terraform apply** provisions registry automatically

### Workflow Inputs

- `registry_name`: Lowercase with hyphens (e.g., `wordpress-platform`)
- `owner`: Team owner (e.g., `app-team-wordpress`)
- `risk`: Risk level (`low`, `medium`, `high`)
- `id`: Registry ID (e.g., `REGISTRY_WORDPRESS_PLATFORM`)
- `environment`: Target environment (`dev`, `test`, `staging`, `prod`)

### Validation Rules

- Registry name: `^[a-z][a-z0-9-]*$`
- Owner: `^app-team-[a-z0-9-]+$`
- ID: `^REGISTRY_[A-Z0-9_]+$`

## Consequences

**Pros:**
- Self-service for app teams (no manual file editing)
- Enforces naming conventions automatically
- Creates audit trail via PRs
- Reduces platform team toil
- Idempotent (safe to re-run)

**Cons:**
- Still requires PR review (not fully automated)
- App teams need GitHub access
- Requires understanding of inputs

**Mitigations:**
- Clear input descriptions in workflow
- Validation errors provide helpful messages
- PR template guides next steps

## Related
- [ADR-0092: ECR Registry Product Strategy](./ADR-0092-ecr-registry-product-strategy.md)
- [ADR-0093: Automated Policy Enforcement](./ADR-0093-automated-policy-enforcement.md)
