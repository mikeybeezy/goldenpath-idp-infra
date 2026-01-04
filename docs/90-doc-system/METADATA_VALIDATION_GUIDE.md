---
id: METADATA_VALIDATION_GUIDE
title: Metadata Validation Runbook
type: runbook
category: 90-doc-system
version: 1.0
owner: platform-team
status: active
dependencies:
- scripts/validate-metadata.py
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to:
- METADATA_BACKFILL_SCRIPT
- RELATIONSHIP_EXTRACTION_SCRIPT
- ADR-0084
- METADATA_STRATEGY
---

## Metadata Validation Runbook

## Overview

This guide explains the `validate-metadata.py` tool used in our CI/CD pipeline.

## The Script

Located at: `scripts/validate-metadata.py`

It enforces the Schema defined in [METADATA_STRATEGY.md](file:///Users/mikesablaze/goldenpath-idp-infra/docs/governance/METADATA_STRATEGY.md) across all Markdown (`.md`) and Sidecar YAML (`metadata.yaml`) files.

## Usage

### Local Run

```bash
# Scan entire repository (Recommended)
python3 scripts/validate-metadata.py .

# Scan specific folder
python3 scripts/validate-metadata.py gitops/helm
```

### CI Integration

This script runs automatically on Pull Requests affecting any `.md` or `metadata.yaml` file via the [Quality - Metadata Validation](file:///Users/mikesablaze/goldenpath-idp-infra/.github/workflows/ci-metadata-validation.yml) workflow.

## Troubleshooting Errors

| Error Message | Meaning | Fix |
| :--- | :--- | :--- |
| `Missing required field: 'owner'` | The YAML header/file is missing the owner key. | Add `owner: platform-team` |
| `ID mismatch` | The ID in the header doesn't match the filename. | Rename file or update ID. |
| `Invalid YAML` | Indentation or syntax error (check for multiple `---`). | Use `yaml.safe_load_all` compatible syntax. |

## Evolution

If we add new required fields, update the `REQUIRED_FIELDS` list in the python script and follow [ADR-0088](file:///Users/mikesablaze/goldenpath-idp-infra/docs/adrs/ADR-0088-automated-metadata-remediation.md) for bulk remediation.
