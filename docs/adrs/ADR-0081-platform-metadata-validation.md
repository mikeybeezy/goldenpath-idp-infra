---
id: ADR-0081
title: Platform Metadata Validation Strategy
type: adr
owner: platform-team
status: active
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
lifecycle:
  supported_until: 2027-01-01
  breaking_change: false
relates_to:
  - ADR-0066
---

# ADR-0081: Platform Metadata Validation Strategy

## Context
As the Golden Path IDP scales, we are introducing a "Knowledge Graph" approach to link artifacts (Code, Docs, Decisions). We need a way to enforce the integrity of these links.

## Options Considered
1.  **Generic Linters (SuperLinter / Yamllint):** Good for syntax, bad for logic.
2.  **Custom Script (`validate-metadata.py`):** Can check business logic and referential integrity.

## Comparison

| Feature | Generic Linter (Yamllint) | Custom Validator (`validate-metadata.py`) |
| :--- | :--- | :--- |
| **Check Type** | Syntax (Formatting) | Semantics (Meaning) |
| **Validation** | "Is this valid YAML?" | "Is this a valid Owner?" |
| **Integrity** | None | Checks if linked ADRs actually exist |
| **Custom Rules** | Limited | Infinite (Python logic) |
| **Maintenance** | Low (Off the shelf) | Medium (Owned code) |

## Decision
We will implment **BOTH**, but rely on the **Custom Validator** for the "Green Gate".
We choose to write and maintain `scripts/validate-metadata.py`.

## Consequences
*   **Positive:** Guaranteed referential integrity. No "Dead Links" in our graph.
*   **Negative:** We must maintain the python script.
