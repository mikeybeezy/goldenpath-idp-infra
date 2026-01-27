---
id: CL-0187-test-proof-generation
title: 'CL-0187: Add test proof generation for script certification'
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
schema_version: 1
relates_to:
  - ADR-0146-schema-driven-script-certification
  - python-tests.yml
  - validate_scripts_tested.py
  - SCRIPT_CERTIFICATION_MATRIX
supersedes: []
superseded_by: []
tags:
  - tdd
  - certification
  - governance
inheritance: {}
supported_until: 2028-01-01
value_quantification:
  vq_class: HV/LQ
  impact_tier: medium
  potential_savings_hours: 4.0
version: '1.0'
breaking_change: false
---

# CL-0187: Add test proof generation for script certification

## Summary

Closes the gap between "tests declared" and "tests actually ran and passed" in the script certification system. CI now generates proof artifacts that link test results to script IDs, enabling verification that scripts with `evidence: ci` have actually passed their tests.

## Problem

Previously, the script certification system could verify:
- ✅ Metadata structure is valid
- ✅ Test file exists
-  Tests actually ran (unknown)
-  Tests passed (unknown)

This gap meant `evidence: declared` was effectively the same as `evidence: ci` - neither verified actual test execution.

## Solution

1. **New script**: `scripts/generate_test_proofs.py`
   - Parses pytest junit.xml output
   - Maps test files to script IDs via metadata
   - Generates proof artifacts: `test-results/proofs/proof-{SCRIPT-ID}.json`

2. **Updated workflow**: `python-tests.yml`
   - Runs pytest with `--junitxml` output
   - Executes proof generator after tests
   - Uploads proof artifacts (retained 90 days)
   - Adds verification job using `--verify-proofs` flag

3. **Proof artifact schema**:
   ```json
   {
     "schema_version": "1.0",
     "script_id": "SCRIPT-XXXX",
     "commit_sha": "abc123",
     "ci_run_id": "12345",
     "test_summary": {
       "total": 5,
       "passed": 5,
       "failed": 0,
       "pass_rate": 100.0
     },
     "verdict": "PASS"
   }
   ```

## Evidence Levels (Updated Meaning)

| Level | Old Meaning | New Meaning |
|-------|-------------|-------------|
| `manual` | Allowed for low-risk | Allowed for low-risk |
| `declared` | Test file exists | Test file exists, not CI-verified |
| `ci` | (unused) | **Proof artifact exists with PASS verdict** |

## Files Changed

- `scripts/generate_test_proofs.py` - New proof generator script
- `.github/workflows/python-tests.yml` - Updated to generate and upload proofs
- `docs/changelog/entries/CL-0187-test-proof-generation.md` - This changelog

## Usage

**Local dry-run**:
```bash
python3 scripts/generate_test_proofs.py --dry-run
```

**Verify with proofs**:
```bash
python3 scripts/validate_scripts_tested.py --verify-proofs
```

## Related

- ADR-0146: Schema-Driven Script Certification
- ADR-0164: Agent Trust and Identity Architecture
- CL-0186: Certification tracking in CI
