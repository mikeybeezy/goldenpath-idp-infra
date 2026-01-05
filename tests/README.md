---
id: TEST_INDEX
title: Platform Testing Index
type: documentation
category: testing
version: '1.0'
owner: platform-team
status: active
dependencies: []
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: '2028-01-01'
  breaking_change: false
relates_to: []
---

# Platform Testing Index

**Purpose:** Track all feature tests, integration tests, and validation results

---

## Feature Tests

### ECR Catalog Generator
**Location:** [feature-tests/ecr-catalog-generator](./feature-tests/ecr-catalog-generator/)  
**Status:** ✅ Passed  
**Date:** 2026-01-05  
**What:** Tests catalog generator displays risk-based security controls

### Risk-Based Policies (Planned)
**Location:** `feature-tests/risk-based-policies/`  
**Status:** Not yet tested  
**What:** Validate Terraform applies correct controls based on risk level

### Self-Service Workflow (Planned)
**Location:** `feature-tests/self-service-workflow/`  
**Status:** Not yet tested  
**What:** End-to-end test of registry creation via GitHub Actions

---

## Integration Tests

### ECR Registry Creation (Planned)
**Location:** `integration-tests/ecr-registry-creation/`  
**Status:** Not yet tested  
**What:** Full workflow from request → PR → Terraform → AWS

---

## Test Guidelines

**When to add a test:**
- New feature implemented
- Bug fix that needs validation
- Critical workflow change

**Test structure:**
```
feature-tests/<feature-name>/
├── test-plan.md          # What we're testing
├── test-data/            # Input fixtures
├── expected-output/      # What should happen
├── actual-output/        # What actually happened
└── test-results.md       # Pass/fail + observations
```

**Naming convention:**
- Feature tests: `feature-tests/<feature-name>/`
- Integration tests: `integration-tests/<workflow-name>/`
