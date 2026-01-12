---
id: GUIDE-002
title: Born Governed Lifecycle
type: guide
relates_to:
  - CNT-001
  - ADR-0146
---

# How It Works: Born Governed Lifecycle

This guide visualizes the **Schema-Driven Script Testing** architecture (ADR-0146).
It explains how a script moves from "Code" to "Certified Asset" using contracts.

## The Architecture

The system consists of four key components working in a closed loop:

```mermaid
graph TD
    Schema[Contract Schema<br/>script.schema.yaml];
    Script[Script Source<br/>Standard Metadata];
    Wrapper[Test Wrapper<br/>bin/test-verified];
    Validator[Enforcer<br/>validate_scripts_tested.py];
    Proof[Proof Artifact<br/>proof-xyz.json];

    Script -->|Must Conform to| Schema;
    Wrapper -->|Reads| Script;
    Wrapper -->|Executes| TestRunner[Pytest / Bats];
    TestRunner -->|If Pass| Proof;
    Validator -->|Verifies| Proof;
    Validator -->|Enforces| Schema;

    style Schema fill:#f9f,stroke:#333,stroke-width:4px
    style Proof fill:#90EE90,stroke:#333,stroke-width:2px
```

---

## The Certification Flow

How verification happens during a standard CI pipeline run:

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Script as Script (Source)
    participant Wrapper as Verified Runner
    participant Schema as Contract
    participant Proof as Proof Artifact
    participant CI as Gatekeeper

    Dev->>Script: Writes Code + Metadata Header
    
    rect rgb(240, 248, 255)
    note right of Dev: Phase 1: Local Verification
    Dev->>Wrapper: bin/test-verified script.py
    Wrapper->>Schema: Validate Contract
    Schema-->>Wrapper: Valid
    Wrapper->>Script: Run Declared Command (pytest)
    Script-->>Wrapper: ✅ Passed
    Wrapper->>Proof: Generate proof-script.json
    end
    
    rect rgb(255, 240, 245)
    note right of CI: Phase 2: CI Certification
    CI->>Validator: validate_scripts_tested.py --verify-proofs
    Validator->>Script: Check Risk Profile
    Validator->>Proof: Check SHA & Run ID
    
    alt Proof Valid
        Validator-->>CI: ✅ Certified (Level 3)
    else Proof Stale/Missing
        Validator-->>CI: ❌ Failed (Level 0)
    end
    end
```

---

## Component Roles

### 1. The Contract (Schema)
**File:** `schemas/automation/script.schema.yaml`
- Defines the "Law".
- Specifies required fields (`id`, `owner`, `test.runner`).
- Defines Maturity Levels (0-3).

### 2. The Standard (Source)
**File:** `scripts/*.py`
- Embeds the contract directly in the header.
- Self-describes its testing needs.

```python
"""
---
id: SCRIPT-001
maturity: 3
test:
  command: "pytest tests/my_test.py"
  evidence: ci
---
"""
```

### 3. The Executor (Wrapper)
**File:** `bin/test-verified`
- The "honest broker".
- Runs the test exactly as declared.
- Mints the `proof.json` artifact (the "Certificate").

### 4. The Enforcer (Validator)
**File:** `scripts/validate_scripts_tested.py`
- The "Auditor".
- Runs in CI/Pre-commit.
- Checks that High Risk scripts actually HAVE a valid proof.

---

## Workflow Integration

| Stage | Action | Tool | Outcome |
| :--- | :--- | :--- | :--- |
| **Development** | Write Code | Editor | Header added |
| **Commit** | Pre-commit | `validate_scripts_tested.py` | Schema compliant? |
| **Test** | Run Tests | `bin/test-verified` | Proof generated |
| **Gate** | CI Validation | `validate_scripts_tested.py --verify-proofs` | **Certified** |
