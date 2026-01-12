---
id: HIW_PR_GUARDRAILS
title: 'How It Works: PR Guardrails'
type: documentation
relates_to:
  - scripts/pr_guardrails.py
  - scripts/validate_enums.py
  - .github/workflows/pr-guardrails.yml
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
- **VQ for Agents**: Mandatory Value Quantification (VQ) is enforced for all AI-generated PRs (e.g., VQ Class: HV/HQ).

## 2. Smart Bypasses (Contextual Logic)
The engine is not a "dumb" gate; it understands context via labels:
- `docs-only`: Bypasses if every changed file is a `.md` file.
- `typo-fix`: Bypasses if total lines changed are less than 50.
- `hotfix`: Bypasses if targeting `main` and authored by the platform team.

## 3. Metadata Injection
For infrastructure-heavy PRs (Terraform/Apps), the engine verifies that a corresponding `metadata.yaml` exists and that its `id` is properly injected as a tag in the actual cloud resource.
