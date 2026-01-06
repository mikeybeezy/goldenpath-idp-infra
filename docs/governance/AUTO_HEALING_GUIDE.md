# 🛡️ Governance: Documentation Auto-Healing Guide

**Status**: Active | **Owner**: Platform-Team | **Last Updated**: 2026-01-06

## 📖 Overview
To maintain a high-integrity developer portal (Backstage) and a clear operational landscape, the platform enforces "Zero-Drift" documentation. This is achieved via a **Closed-Loop Auto-Healing** mechanism that ensures indices for scripts and workflows are always in sync with the physical state of the repository.

## 🔄 The Auto-Healing Flow

```text
  Developer Action             CI/CD Quality Gate (Auto-Healer)
  +----------------+           +----------------------------------+
  |                |           |                                  |
  |  Add new script|           |  1. Trigger on PR Push           |
  |  or workflow   |---------->|                                  |
  |                |           |  2. Scan repository files        |
  +----------------+           |                                  |
           |                   |  3. Validate against Index files |
           |                   |     (Drift Detected?)            |
           |                   |           |                      |
           |                   |           |-- [YES] -------------|
           |                   |           |                      |
           |                   |           v                      |
           |                   |  4. Execute Index Generators     |
           |                   |                                  |
           |                   |  5. Commit fixes back to PR      |
           |<------------------|     (github-actions[bot])        |
           |                   |                                  |
  +----------------+           |  6. Re-validate Final State      |
  |                |           |                                  |
  | PR updated with|           |  7. Pass PR Gate ✅               |
  | latest docs    |           |                                  |
  +----------------+           +----------------------------------+
```

## ⚖️ PR Review & Gate Mechanics

### Who reviews the PR?
- **Primary**: The `platform-team` is the designated owner for all governance and automation indices.
- **Enforcement**: This is managed via the `CODEOWNERS` file, which requires approval from the platform team for any changes to `scripts/index.md` or `ci-workflows/CI_WORKFLOWS.md`.

### How does it pass the gate?
The PR gate is managed by the `.github/workflows/ci-index-auto-heal.yml` workflow and relies on a **Success/Failure contract**:

1.  **Strict Validation**: The workflow runs `generate_script_index.py --validate` and `generate_workflow_index.py --validate`.
2.  **Exit Code Policy**: 
    - **Exit 0**: The index matches the physical files. The gate turns **GREEN** ✅.
    - **Exit 1**: Drift is detected. The workflow attempts to auto-heal.
3.  **The "Safety Loop"**: After the bot commits the updated indices, the workflow runs the validation **one final time**.
    - If the second validation confirms the index is now perfect, the gate turns **GREEN** ✅.
    - If it still fails (indicating a deeper script error), the gate stays **RED** ❌ and blocks the merge.

## 🛠️ Key Components
1.  **Enforcement Script**: `scripts/generate_script_index.py --validate`
2.  **Workflow Scraper**: `scripts/generate_workflow_index.py --validate`
3.  **The Healer**: `.github/workflows/ci-index-auto-heal.yml`

## 🚦 Operational Rules
- **Automatic**: No manual action is required. If drift is detected, the bot commits the fix.
- **Atomic**: The healer only updates index files; it never touches logic or configuration.
- **Traceable**: All automated doc updates are committed with `chore: auto-heal documentation indices [skip ci]`.
