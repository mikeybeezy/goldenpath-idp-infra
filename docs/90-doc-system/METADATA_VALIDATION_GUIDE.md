---
id: DOC-002
title: Metadata Validation Runbook
type: runbook
owner: platform-team
status: active
---

## Metadata Validation Runbook

## Overview
This guide explains the `validate-metadata.py` tool used in our CI/CD pipeline.

## The Script
Located at: `scripts/validate-metadata.py`

It scans the `docs/` directory and enforces the Schema defined in `METADATA_STRATEGY.md`.

## Usage

### Local Run
```bash
# Scan entire doc tree
python3 scripts/validate-metadata.py docs

# Scan specific folder
python3 scripts/validate-metadata.py docs/adrs
```

### CI Integration
This script runs automatically on Pull Requests affecting `docs/**`.

## Troubleshooting Errors

| Error Message | Meaning | Fix |
| :--- | :--- | :--- |
| `Missing required field: 'owner'` | The YAML header is missing the owner key. | Add `owner: platform-team` |
| `ID mismatch` | The ID in the file header doesn't match the filename. | Rename file or update ID. |
| `Invalid YAML` | Indentation or syntax error. | Check your spaces/colons. |

## Evolution
If we add new required fields (e.g., `cost_center`), update the `REQUIRED_FIELDS` list in the python script.
