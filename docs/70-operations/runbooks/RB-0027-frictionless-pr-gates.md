---
id: RB-0027
title: Frictionless PR Gates (Heal-First Workflow)
type: runbook
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
category: runbooks
relates_to:
  - 00_START_HERE
  - 24_PR_GATES
  - CL-0112
  - DOCS_RUNBOOKS_README
  - GOLDENPATH_IDP_ROOT_README
  - PR_GUARDRAILS
---
# RB-0027: Frictionless PR Gates (Heal-First Workflow)

## Context
The Golden Path IDP enforces 15+ governance gates via pre-commit hooks and CI checks. To minimize developer friction and prevent "fighting the machine," this runbook outlines the **Heal-First, Push-Once** workflow.

## 🚀 The "Golden Path" Workflow
Follow this sequence to ensure your PR passes all gates on the first attempt.

### 1. Standardize (The Healer)
The platform provides a remediation engine that automatically formats YAML, injects missing metadata, and aligns files with the platform dialect.
```bash
bin/governance heal .
```

### 2. Auto-Generate Indices
We use **Marker-Based Indexing**. Do not edit index tables manually. Run the generation scripts (or let the pre-commit hook do it):
```bash
# Handled automatically by pre-commit, or run manually:
python3 scripts/generate_script_index.py
python3 scripts/generate_workflow_index.py
```

### 3. Local Verification
Run the pre-commit suite locally to catch errors before they hit CI.
```bash
python3 -m pre_commit run --all-files
```

### 4. Push with Confidence
```bash
git add .
git commit -m "feat: my change"
git push origin <branch>
```

## 🤖 Internal Logic (For Agents)
- **Dialect Alignment**: All automation scripts use `lib/metadata_config.py` to ensure YAML output matches `yamllint` expectations.
- **Specific Owner Wins**: If a specific `goldenpath.idp/id` exists in a K8s manifest, the healer will *not* overwrite it with generic environment metadata.
- **Marker Injection**: Generation scripts only touch content between `<!-- START -->` and `<!-- END -->` markers to preserve hand-managed frontmatter.

## Troubleshooting
- **Oscillation**: If CI reports changes even after a local heal, ensure you are not manually editing the `governance` blocks in K8s manifests; use the source `metadata.yaml` instead.
- **Index Drift**: If an index is out of sync, ensure your markers are intact.
