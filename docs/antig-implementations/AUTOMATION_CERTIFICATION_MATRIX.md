---
id: AUTOMATION_CERTIFICATION_MATRIX
title: Automation Certification Master Record
type: documentation
owner: platform-team
status: active
category: governance
---

# Automation Certification Matrix (Master Record)


This ledger tracks the verification results for every script in the repository. Scripts must fulfill all requirements within a column to be "Certified" for that surface area.

---

## Certification Requirements (The Five Pillars)

| Pillar | Requirement | Verification Method |
| :--- | :--- | :--- |
| **Logic** | - Passed `ruff` / `yamllint`<br>- Functional Unit/Feature Tests exist<br>- Graceful exit on errors | `scripts/test_platform_health.py` |
| **Safety** | - Supports `--dry-run`<br>- Verified Idempotency (2nd run is no-op)<br>- Temp files cleaned up | Manual / CI Logs |
| **Context** | - Linked to ADR/CL (Traceable)<br>- VQ Class assigned<br>- Heartbeat integrated | `check_script_traceability.py` |
| **Human** | - `--help` is descriptive<br>- Structured log output<br>- `owner` tag exists | Manual Audit |
| **System** | - Part of CI/CD Guardrails<br>- Multi-environment verified<br>- Rollback plan documented | `pr_guardrails.py` |

---

## Script Certification Status

| Script | Logic | Safety | Context | Human | System | Rating |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `validate_metadata.py` | ✅ | ✅ | ✅ | ✅ | ✅ |  |
| `standardize_metadata.py` | ✅ | ✅ | ✅ | ✅ | ✅ |  |
| `platform_health.py` | ✅ | ⚠️ | ✅ | ✅ | ✅ |  |
| `check_script_traceability.py` | ✅ | ✅ | ✅ | ✅ | ✅ |  |
| `validate_enums.py` | ✅ | ✅ | ✅ | ✅ | ✅ |  |
| `pr_guardrails.py` | ✅ | ✅ | ✅ | ✅ | ✅ |  |
| `audit_metadata.py` | ✅ | ⚠️ | ✅ | ✅ | ⚠️ |  |
| `backfill_metadata.py` | ✅ | ⚠️ | ✅ | ✅ | ⚠️ |  |
| `check_compliance.py` | ✅ | ⚠️ | ✅ | ✅ | ⚠️ |  |
| `check_doc_freshness.py` | ⚠️ | ⚠️ | ✅ | ✅ | ⚠️ |  |
| `check_doc_index_contract.py` | ⚠️ | ⚠️ | ✅ | ✅ | ⚠️ |  |
| `ecr-build-push.sh` | ⚠️ | ⚠️ | ✅ | ✅ | ⚠️ |  |
| `enforce_emoji_policy.py` | ✅ | ✅ | ✅ | ✅ | ✅ |  |
| `extract_relationships.py` | ⚠️ | ⚠️ | ✅ | ✅ | ⚠️ |  |
| `fix_yaml_syntax.py` | ⚠️ | ⚠️ | ✅ | ✅ | ⚠️ |  |
| `format_docs.py` | ⚠️ | ⚠️ | ✅ | ✅ | ⚠️ |  |
| `generate-build-log.sh` | ⚠️ | ⚠️ | ✅ | ✅ | ⚠️ |  |
| `generate-teardown-log.sh` | ⚠️ | ⚠️ | ✅ | ✅ | ⚠️ |  |
| `generate_adr_index.py` | ✅ | ✅ | ✅ | ✅ | ✅ |  |
| `generate_catalog_docs.py` | ✅ | ✅ | ✅ | ✅ | ✅ |  |
| `generate_governance_vocab.py` | ✅ | ✅ | ✅ | ✅ | ✅ |  |
| `generate_script_index.py` | ✅ | ✅ | ✅ | ✅ | ✅ |  |
| `generate_workflow_index.py" | ✅ | ✅ | ✅ | ✅ | ✅ |  |
| `lib/metadata_config.py` | ✅ | N/A | ✅ | ✅ | ✅ |  |
| `lib/vq_logger.py` | ✅ | ✅ | ✅ | ✅ | ✅ |  |
| `migrate_partial_metadata.py` | ⚠️ | ⚠️ | ✅ | ✅ | ⚠️ |  |
| `policy-enforcement/check-policy-compliance.py` | ⚠️ | ⚠️ | ✅ | ✅ | ⚠️ |  |
| `reliability-metrics.sh` | ⚠️ | ⚠️ | ✅ | ✅ | ⚠️ |  |
| `render_template.py` | ⚠️ | ⚠️ | ✅ | ✅ | ⚠️ |  |
| `resolve-cluster-name.sh` | ⚠️ | ⚠️ | ✅ | ✅ | ⚠️ |  |
| `scaffold_ecr.py` | ⚠️ | ⚠️ | ✅ | ✅ | ⚠️ |  |
| `sync_backstage_entities.py" | ⚠️ | ⚠️ | ✅ | ✅ | ⚠️ |  |
| `test_hotfix.py` | ✅ | ✅ | ✅ | ✅ | ✅ |  |
| `test_platform_health.py` | ✅ | ✅ | ✅ | ✅ | ✅ |  |
| `validate_routing_compliance.py` | ⚠️ | ⚠️ | ✅ | ✅ | ⚠️ |  |

---
**Legend**: ✅ = Certified | ⚠️ = Needs Audit |  = Failed | N/A = Not Applicable
