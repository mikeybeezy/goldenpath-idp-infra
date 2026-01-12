---
id: CNT-001
title: Script Standard (Born Governed)
type: contract
relates_to:
  - ADR-0146
  - schema:automation/script.schema.yaml
version: 1.0
---

# Script Standard (Born Governed)

## Goal
Every script in the platform must be **"Born Governed"**. This means it is not just code, but a managed asset that:
- Carries embedded metadata (Self-describing)
- Supports dry-run (Safety by default)
- Declares a test command (Testable contract)
- Passes validation gates (Machine-enforced quality)

## Required Metadata Block

Every verifiable script must start with a YAML metadata block embedded in its native comment format.

### Python
```python
"""
---
id: SCRIPT-0001
type: script
owner: platform-team
status: active
maturity: 2
dry_run:
  supported: true
test:
  runner: pytest
  command: "pytest -q tests/scripts/test_script_0001.py"
  evidence: declared
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
---
"""
```

### Bash
```bash
# ---
# id: SCRIPT-0001
# type: script
# owner: platform-team
# status: active
# maturity: 2
# dry_run:
#   supported: true
# test:
#   runner: shellcheck
#   command: "shellcheck scripts/my_script.sh"
#   evidence: declared
# risk_profile:
#   production_impact: low
#   security_risk: low
#   coupling_risk: low
# ---
```

## Maturity Levels

This standard defines explicit quality gates based on maturity `[0-3]`.

| Level | Name | Requirements | Allowed Usage |
| :--- | :--- | :--- | :--- |
| **0** | **Ungoverned** | No metadata, no test, no dry-run. | ❌ Blocked by CI |
| **1** | **Tracked** | Metadata present + Lintable. | ✅ Experimental / Local Only |
| **2** | **Validated** | Metadata + Dry-Run supported + Test command declared. | ✅ Standard Automation |
| **3** | **Certified** | All of Level 2 + **CI Proof** required for Med/High risk scripts. | ✅ High-Impact / Critical Path |

## Compliance
Enforcement is handled by `scripts/validate_scripts_tested.py`.
- **Level 0**: Scripts without headers are flagged immediately.
- **Level 3**: Scripts claiming Level 3 or High Risk must produce a `proof-*.json` artifact in CI.

## Field Definitions

| Field | Description | Values |
| :--- | :--- | :--- |
| `id` | Unique Identifier | `SCRIPT-XXXX` or snake_case name |
| `dry_run.supported` | Does it implement `--dry-run`? | `true` / `false` |
| `test.evidence` | How is testing verified? | `declared` (trust me), `ci` (machine proof), `manual` |
| `risk_profile` | Impact analysis | `none`, `low`, `medium`, `high` |
