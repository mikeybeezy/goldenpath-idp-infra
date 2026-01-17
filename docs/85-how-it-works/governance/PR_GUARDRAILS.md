---
id: PR_GUARDRAILS
title: 'How It Works: PR Guardrails'
type: documentation
relates_to:
  - PR_GUARDRAILS_INDEX
  - RB-0027
---
# How It Works: PR Guardrails

This document explains how the platform enforces quality, traceability, and governance on every Pull Request using the "Guardrails" engine.

## 0. The Gatekeeper Architecture
The guardrails act as a "Bouncer," ensuring that no code or configuration enters the repository without meeting the platform's metadata and checklist standards.

```text
+---------------+       +-----------------------+
|   Developer   | ----> |   Git Push (PR)       |
+---------------+       +-----------------------+
                                    |
                        ( 1. Trigger GitHub Action )
                                    |
            +-----------------------+-------+-----------------------+
            |                               |                       |
+-----------------------+       +-----------------------+   +-----------------------+
|  Checklist Validation |       |  Bypass Logic Labels  |   | Script Traceability   |
+-----------------------+       +-----------------------+   +-----------------------+
            |                               |                       |
            +-----------------------+-------+-----------------------+
                                    |
                        ( 2. Exit Status: 0 or 1 )
                                    |
+-----------------------+           |
|   PR Blocked/Allowed  | <---------+
+-----------------------+
```

## 1. The Validation Engine (`pr_guardrails.py`)
The core logic resides in a specialized Python engine that reads the PR body, labels, and author metadata.

- **Checklist Enforcement**: Rejects PRs if mandatory sections (Change Type, Impact, Testing) are not checked in the PR description.
- **Traceability Gate**: Uses `check_script_traceability.py` to ensure any new scripts are documented in an ADR and added to a Changelog.

### Script Traceability
To eliminate **"Dark Automation"**, the platform enforces that every automation script must have a recorded provenance.

- **The "Why" (ADRs)**: Every script must be referenced in an **Architectural Decision Record** (`docs/adrs/`). This proves the script was created as part of a formal designer intent.
- **The "When" (Changelog)**: Every script must be mentioned in at least one **Changelog entry** (`docs/changelog/entries/`). This provides a historical audit trail of its introduction and evolution.

**How it works**:
The `scripts/check_script_traceability.py` auditor scans the `scripts/` directory for `.py` and `.sh` files. It then cross-references each filename against the entire markdown corpus in the ADR and Changelog directories. If a script is found to be "orphaned" (missing either an ADR or a CL link), the PR gate is blocked.
- **VQ for Agents**: Mandatory Value Quantification (VQ) is enforced for all AI-generated PRs (e.g., VQ Class: HV/HQ).

## 2. Smart Bypasses (Contextual Logic)
The engine is not a "dumb" gate; it understands context via labels:
- `docs-only`: Bypasses if every changed file is a `.md` file.
- `typo-fix`: Bypasses if total lines changed are less than 50.
- `hotfix`: Bypasses if targeting `main` and authored by the platform team.

## 3. Metadata Injection
For infrastructure-heavy PRs (Terraform/Apps), the engine verifies that a corresponding `metadata.yaml` exists and that its `id` is properly injected as a tag in the actual cloud resource.

## 4. Automated Remediation (Reducing Friction)
To prevent "gate fatigue," the platform provides **Remediation Engines**:
- **`bin/governance heal`**: Automatically reformats YAML and Markdown to meet strict `yamllint` and `markdownlint` standards.
- **Marker-Based Indexing**: Replaces manual table maintenance with automated generation between safe comment markers.
- **CI Auto-Healer**: A GitHub Action that automatically commits fixes for minor index drift on behalf of the developer.

Refer to [**RB-0027: Frictionless PR Gates**](../docs/70-operations/runbooks/RB-0027-frictionless-pr-gates.md) for the recommended developer workflow.
