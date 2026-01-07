---
id: TEST_INDEX
title: Platform Testing Index
type: documentation
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to: []
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
category: testing
version: '1.0'
supported_until: '2028-01-01'
breaking_change: false
---

# Platform Testing Index

**Purpose:** Track all feature tests, integration tests, and validation results

---

## Unit Tests

### Metadata Inheritance Engine
**Location:** [unit/test_metadata_inheritance.py](./unit/test_metadata_inheritance.py)
**Status:** ✅ 3/3 Passing
**Coverage:** `MetadataConfig` core inheritance logic
**CI:** Automated via [python-tests.yml](../../.github/workflows/python-tests.yml)

### Metadata Validation Engine
**Location:** [unit/test_validate_metadata.py](./unit/test_validate_metadata.py)
**Status:** ✅ 7/7 Passing
**Coverage:** 
- Injection verification (inline & governance block patterns)
- YAML/Markdown frontmatter extraction
- Error handling

**CI:** Automated via [python-tests.yml](../../.github/workflows/python-tests.yml)

### Value Quantification Logger
**Location:** [unit/test_vq_logger.py](./unit/test_vq_logger.py)
**Status:** ✅ 3/3 Passing
**Coverage:**
- ROI ledger reads
- Script value metadata lookup
- Numeric validation

**CI:** Automated via [python-tests.yml](../../.github/workflows/python-tests.yml)

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

## Running Tests

### Unit Tests (Automated in CI)
```bash
# Run all unit tests
python3 -m unittest discover -s tests/unit -p "test_*.py" -v

# Run specific test module
python3 tests/unit/test_metadata_inheritance.py -v
```

### Test Coverage Stats
- **Total Modules:** 3
- **Total Tests:** 13
- **Pass Rate:** 100%
- **CI Integration:** ✅ GitHub Actions

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
- Unit tests: `tests/unit/test_<module>.py`
