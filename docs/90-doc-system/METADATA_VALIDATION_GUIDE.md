---
id: METADATA_VALIDATION_GUIDE
title: Metadata Validation Runbook
type: runbook
domain: platform-core
applies_to: []
owner: platform-team
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
relates_to:
  - METADATA_BACKFILL_SCRIPT
  - RELATIONSHIP_EXTRACTION_SCRIPT
  - ADR-0084
  - METADATA_STRATEGY
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
category: governance
status: active
version: 1.0
dependencies:
  - scripts/validate_metadata.py
supported_until: 2028-01-01
breaking_change: false
---

## Metadata Validation Runbook

## Overview

This guide explains the `validate_metadata.py` tool used in our CI/CD pipeline.

## The Script

Located at: `scripts/validate_metadata.py`

It enforces the Schema defined in [METADATA_STRATEGY.md](docs/10-governance/METADATA_STRATEGY.md) across all Markdown (`.md`) and Sidecar YAML (`metadata.yaml`) files.

## Authoring Flow (Recommended)

1. **Scaffold** new docs using `scripts/scaffold_doc.py` (generates compliant frontmatter).
2. **Auto-fix** runs in pre-commit via `scripts/standardize_metadata.py` for changed docs.
3. **Validate** in CI using `scripts/validate_metadata.py` (backstop only).

## Usage

### Local Run

```bash
# Scan entire repository (Recommended)
python3 scripts/validate_metadata.py .

# Scan specific folder
python3 scripts/validate_metadata.py gitops/helm
```

### CI Integration

This script runs automatically on Pull Requests affecting any `.md` or `metadata.yaml` file via the [Quality - Metadata Validation](.github/workflows/ci-metadata-validation.yml) workflow.

## Troubleshooting Errors

| Error Message | Meaning | Fix |
| :--- | :--- | :--- |
| `Missing required field: 'owner'` | The YAML header/file is missing the owner key. | Add `owner: platform-team` |
| `ID mismatch` | The ID in the header doesn't match the filename. | Rename file or update ID. |
| `Invalid YAML` | Indentation or syntax error (check for multiple `---`). | Use `yaml.safe_load_all` compatible syntax. |

## Evolution

If we add new required fields, update the `REQUIRED_FIELDS` list in the python script and follow [ADR-0088](docs/adrs/ADR-0088-automated-metadata-remediation.md) for bulk remediation.
