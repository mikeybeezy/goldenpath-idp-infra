---
id: GITHUB_WORKFLOWS_INDEX
title: GitHub Actions Workflows Index
type: documentation
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: high
  security_risk: medium
  coupling_risk: high
reliability:
  rollback_strategy: git-revert
  observability_tier: gold
  maturity: 1
schema_version: 1
relates_to:
  - ADR-0093
  - ADR-0101
  - CL-0053
  - CL-0063
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
version: '1.0'
dependencies:
  - github-actions
  - terraform
  - aws-cli
supported_until: 2028-01-01
breaking_change: false
---

# GitHub Actions Workflows

## Policy & Governance

### policy-enforcement.yml
**Purpose:** Daily automated policy compliance checks
**Trigger:** Daily at 09:00 UTC + manual
**What it does:**
- Loads policies from `docs/policies/*.yaml`
- Checks all ECR registries against policy rules
- Generates compliance report
- Creates GitHub issues for violations
- Sends Slack alerts

**Status:**  Planned (workflow created, scripts pending)

### create-ecr-registry.yml
**Purpose:** Self-service ECR registry creation
**Trigger:** Manual (workflow_dispatch)
**What it does:**
- Auto-generates registry ID from name (no manual input)
- Validates registry inputs (name, owner, risk)
- Updates registry catalog YAML
- Syncs catalog documentation automatically
- Validates Terraform HCL syntax (`terraform fmt`)
- Updates Terraform tfvars
- Creates PR with Day Zero guidance links

**Status:** ✅ Active
**Related:** [ADR-0100](../docs/adrs/ADR-0100-standardized-ecr-lifecycle-and-documentation.md)

### adr-policy.yml
**Purpose:** Enforce ADR requirements on PRs
**Trigger:** Pull requests
**What it does:** Validates ADR metadata and format

### changelog-policy.yml
**Purpose:** Enforce changelog requirements on PRs
**Trigger:** Pull requests
**What it does:** Validates changelog entries

### branch-policy.yml
**Purpose:** Enforce branch naming conventions
**Trigger:** Pull requests
**What it does:** Validates branch names

---

## Infrastructure

### infra-terraform-apply-dev.yml
**Purpose:** Apply Terraform changes to dev environment
**Trigger:** Push to main, manual

### infra-terraform-apply-test.yml
**Purpose:** Apply Terraform changes to test environment
**Trigger:** Manual

### infra-terraform-apply-staging.yml
**Purpose:** Apply Terraform changes to staging environment
**Trigger:** Manual

### infra-terraform-apply-prod.yml
**Purpose:** Apply Terraform changes to prod environment
**Trigger:** Manual

### pr-terraform-plan.yml
**Purpose:** Run terraform plan on PRs
**Trigger:** Pull requests

---

## Operations

### ci-teardown.yml
**Purpose:** Teardown infrastructure
**Trigger:** Manual

### ci-orphan-cleanup.yml
**Purpose:** Clean up orphaned resources
**Trigger:** Manual

### ci-managed-lb-cleanup.yml
**Purpose:** Clean up managed load balancers
**Trigger:** Manual

### ci-force-unlock.yml
**Purpose:** Force unlock Terraform state
**Trigger:** Manual

---

## Quality & Validation

### pr-guardrails.yml
**Purpose:** PR validation checks
**Trigger:** Pull requests

### pr-labeler.yml
**Purpose:** Auto-label PRs based on changed files
**Trigger:** Pull requests

### super-linter.yml
**Purpose:** Lint code
**Trigger:** Manual

### yamllint.yml
**Purpose:** Lint YAML files
**Trigger:** Pull requests (main only)

### pre-commit.yml
**Purpose:** Run pre-commit hooks
**Trigger:** Pull requests (main only)

### ci-metadata-validation.yml
**Purpose:** Validate and auto-heal metadata schema
**Trigger:** Pull requests (on `.md`, `.yaml`, `.yml` changes)
**What it does:**
- Validates only files changed in the PR (scoped validation)
- Auto-heals metadata issues using `standardize_metadata.py`
- Auto-commits fixes with `[skip ci]` to prevent loops
- Skips validation for exempt labels

**Exempt Labels:**
| Label | Use Case |
| :--- | :--- |
| `governance-exempt` | General bypass for platform exceptions |
| `buildid` | CI/infrastructure pipeline PRs |
| `docs-only` | Documentation-only changes |
| `typo-fix` | Trivial text corrections |
| `hotfix` | Emergency patches |

**Status:** ✅ Active
**Related:** [ADR-0101](../docs/adrs/ADR-0101-pr-metadata-auto-heal.md)

### doc-freshness.yml
**Purpose:** Check documentation freshness
**Trigger:** Schedule

### quality-platform-health.yaml
**Purpose:** Platform health checks
**Trigger:** Schedule

---

## Application Scaffolding

### repo-scaffold-app.yml
**Purpose:** Scaffold new application repositories
**Trigger:** Manual, Backstage

### ci-backstage.yml
**Purpose:** Backstage CI/CD
**Trigger:** Push

---

## Production Readiness

### production-readiness-review.yml
**Purpose:** Production readiness checklist
**Trigger:** Manual

---

## Total Workflows: 29
