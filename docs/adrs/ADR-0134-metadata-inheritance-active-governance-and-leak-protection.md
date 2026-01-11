---
id: ADR-0134-metadata-inheritance-active-governance-and-leak-protection
title: metadata
type: adr
---

id: ADR-0134-metadata-inheritance-active-governance-and-leak-protection
title: 'ADR-0134: Metadata Inheritance, Active Governance, and Leak Protection'
type: adr
owner: platform-team---

# ADR-0134: Metadata Inheritance, Active Governance, and Leak Protection

## Status
Accepted

## Context
As we reach V1 readiness for the Golden Path IDP, we need a metadata system that is both robust and fluid. Maintaining 500+ explicit metadata files is a velocity bottleneck, while a static "set and forget" governance model risks becoming stale. Furthermore, developers need "scratchpad" zones that don't trigger constant governance nagging, but these zones must never reach production.

## Decision
We have implemented **Cascading Metadata Inheritance** paired with an **Active Governance Loop** and **Leak Protection**.

### 1. Cascading Inheritance (Dry Governance)
- Resources inherit metadata (owner, domain, reliability) from parent `metadata.yaml` files.
- **Identity Rule**: Every asset must still declare a unique `id` locally.
- **Pruning Logic**: Automation (`standardize_metadata.py`) now automatically removes redundant fields from children if they match the parent default, keeping the repository DRY.

### 2. Safety Valve & Leak Protection
- **`exempt: true`**: A new flag that allows developers to bypass strict governance checks for temporary scratchpads.
- **Leak Protection**: The quality gate (`validate_metadata.py`) explicitly blocks any PR where a resource marked as `exempt: true` is bound for the `envs/prod/` or `apps/prod/` zones.

### 3. Active Governance Loop
- **Automated Audit**: A recurring process (`audit_metadata.py`) validates all artifacts and generates immutable health snapshots.
- **Governance Vocabulary**: Auto-generated human-readable documentation ([GOVERNANCE_VOCABULARY.md](docs/10-governance/GOVERNANCE_VOCABULARY.md)) ensures stakeholders are always aligned on valid enums.

### 4. Local DX Helper
- A new `bin/governance` binary provides developers with instant local feedback (`governance check`) before they push to CI.

## Consequences

### Positive
- **Boilerplate Reduction**: ~85% reduction in redundant metadata lines.
- **Velocity**: "Zero-Touch" auto-healing initializes new folders instantly via CI auto-commits.
- **Safety**: Ungoverned scratchpads are programmatically forbidden from reaching production.

### Negative
- **Validation Complexity**: The engine now performs O(depth) recursive lookups.
- **Binary Dependency**: Developers are encouraged to use the `bin/governance` wrapper for the best experience.
