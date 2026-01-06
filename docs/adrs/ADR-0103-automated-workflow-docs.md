---
id: ADR-0103
title: Automated CI Workflow Documentation
status: superseded
superseded_by: ADR-0111
owner: platform-team
created_date: 2026-01-06
supersedes: []
relates_to:
  - ADR-0071 (Doc Taxonomy)
  - ci-workflows/CI_WORKFLOWS.md
---

# ADR-0103: Automated CI Workflow Documentation

## Context
As the complexity of the platform grows, the number of GitHub Actions workflows has increased significantly (>30 workflows). Maintaining a manual index of these workflows (`ci-workflows/CI_WORKFLOWS.md`) leads to documentation drift, where new workflows are added but not documented, or deleted workflows remain in the index.

Manual updates are error-prone and rely on human discipline, which is not scalable. We need a way to ensure the "map" of our CI/CD capabilities is always accurate and auto-generated from the source of truth (the YAML definitions).

## Decision
We will automate the generation of the CI Workflows Index using a Python script (`scripts/generate_workflow_index.py`).

1.  **Source of Truth**: The `.github/workflows/*.yml` files are the single source of truth.
2.  **Metadata Extraction**: The script will parse YAML headers (Name, On) and comments (e.g., `# Owner: platform`) to build the documentation.
3.  **Categorization**: Workflows will be automatically grouped into logical domains (Policy, Plan, Apply, Ops, Bootstrap) based on naming conventions.
4.  **Visualization**: The output will include an ASCII tree view for quick navigation.

## Consequences
### Positive
- **Zero Drift**: Documentation is always 1:1 with code.
- **Discoverability**: New workflows are instantly visible in the index.
- **Standardization**: Enforces the need for proper `name` and consistent file naming to ensure correct categorization.

### Negative
- **Dependency**: Documentation generation now requires Python and the `PyYAML` dependency.
- **Convention**: Workflows named poorly may end up in "Uncategorized" buckets until renamed.

## Implementation
- Script: `scripts/generate_workflow_index.py`
- Output: `ci-workflows/CI_WORKFLOWS.md`
