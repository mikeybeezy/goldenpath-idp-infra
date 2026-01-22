---
id: PRE_COMMIT_CHECKLIST
title: Pre-Commit and Pre-Merge Checklist
type: documentation
domain: governance
owner: platform-team
lifecycle: active
status: active
schema_version: 1
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - PR_GUARDRAILS_INDEX
  - 04_PR_GUARDRAILS
  - 07_AI_AGENT_GOVERNANCE
---

# Pre-Commit and Pre-Merge Checklist

Reference guide for all checks required before committing and merging code.

---

## Quick Command Summary

```bash
# Run all pre-commit checks
pre-commit run --all-files

# Run individual healing scripts
python3 scripts/standardize_metadata.py docs/
python3 scripts/generate_adr_index.py
python3 scripts/generate_script_index.py
python3 scripts/generate_workflow_index.py
python3 scripts/generate_script_matrix.py

# Validation checks
python3 scripts/validate_scripts_tested.py scripts/
python3 scripts/validate_metadata.py docs/

# Check for secrets
gitleaks detect --redact
```

---

## Pre-Commit Hooks (Automatic)

These run automatically on `git commit` if pre-commit is installed:

| Hook | Purpose | Files Affected |
|------|---------|----------------|
| `end-of-file-fixer` | Ensure files end with newline | All files |
| `trailing-whitespace` | Remove trailing whitespace | All files |
| `terraform_fmt` | Format Terraform files | `*.tf` |
| `markdownlint` | Lint markdown files | `*.md` |
| `gitleaks` | Detect secrets/credentials | All files |
| `doc-metadata-autofix` | Standardize doc frontmatter | `docs/**/*.md` |
| `emoji-enforcer` | Check emoji policy | `*.md`, `*.yaml`, `*.yml` |
| `generate-adr-index` | Regenerate ADR index | Always runs |
| `generate-script-index` | Regenerate script index | Always runs |
| `generate-workflow-index` | Regenerate workflow index | Always runs |
| `generate-script-matrix` | Regenerate script matrix | Always runs |
| `validate-script-governance` | Validate script metadata | `scripts/*.py`, `scripts/*.sh` |

---

## Healing Scripts (Run Manually When Needed)

### Metadata Standardization

```bash
python3 scripts/standardize_metadata.py docs/
```

Fixes:
- Missing frontmatter fields
- Incorrect schema versions
- Missing relates_to references

### Index Generation

```bash
python3 scripts/generate_adr_index.py      # ADR index
python3 scripts/generate_script_index.py   # Script index
python3 scripts/generate_workflow_index.py # Workflow index
python3 scripts/generate_script_matrix.py  # Script certification matrix
```

### Backstage Catalog Sync

```bash
python3 scripts/generate_backstage_docs.py    # Sync docs to Backstage
python3 scripts/generate_catalog_docs.py      # Generate catalog docs
```

---

## PR Guardrails (CI Checks)

### Blocking Checks (Must Pass)

| Check | Trigger | What It Validates |
|-------|---------|-------------------|
| **PR Guardrails** | All PRs | Checklist completion, template header, script traceability |
| **Branch Policy** | PRs to main | Only development/build/hotfix branches allowed |
| **ADR Policy** | `adr-required` label | ADR file must be present |
| **Changelog Policy** | `changelog-required` label | Changelog entry must be present |
| **RDS Request Validation** | RDS request changes | Schema compliance |
| **Session Capture Guard** | Session capture changes | Append-only enforcement |
| **Session Log Required** | Critical path changes | Session docs must be updated |

### Warning Checks (Non-Blocking)

| Check | Trigger | What It Validates |
|-------|---------|-------------------|
| **RDS Size Approval** | RDS size changes | Large/XLarge requires approval |
| **RDS tfvars Drift** | tfvars changes | Coupled/standalone sync |

---

## Critical Path Files (Require Session Docs)

Changes to these paths require session capture and summary updates:

```text
.github/workflows/**
gitops/**
bootstrap/**
modules/**
scripts/**
docs/10-governance/**
docs/adrs/**
docs/70-operations/runbooks/**
```

---

## PR Checklist Template

When creating a PR, ensure the body includes:

```markdown
## Change Type
- [ ] Feature
- [ ] Bug Fix
- [ ] Documentation
- [ ] Refactor

## Impact
- [ ] Breaking Change
- [ ] Non-Breaking Change
- [ ] Infrastructure Change

## Testing
- [ ] Unit Tests Pass
- [ ] Integration Tests Pass (if applicable)
- [ ] Manual Testing Completed

## Rollback
- [ ] Rollback Plan Documented
- [ ] No Rollback Needed
```

---

## Bypass Labels

Use these labels to bypass specific checks when appropriate:

| Label | Bypasses |
|-------|----------|
| `docs-only` | Script traceability check |
| `typo-fix` | Full checklist validation |
| `hotfix` | Normal branch policy |
| `build_id` | PR template requirements |
| `changelog-exempt` | Changelog policy check |

---

## Pre-Push Verification Script

Run this before pushing to catch common issues:

```bash
#!/bin/bash
echo "=== Pre-Push Verification ==="
echo ""
echo "1. Running pre-commit hooks..."
pre-commit run --all-files
echo ""
echo "2. Checking for uncommitted changes..."
git status --short
echo ""
echo "3. Verifying branch..."
git branch --show-current
echo ""
echo "4. Recent commits..."
git log --oneline -5
echo ""
echo "=== Verification Complete ==="
```

---

## Common Issues and Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| `markdownlint` fails | MD004 (list style) | Use `*` not `-` for lists |
| `doc-metadata-autofix` changes | Missing fields | Let hook fix or run standardize |
| `gitleaks` fails | Potential secret | Remove credential, use env var |
| `terraform_fmt` fails | Formatting | Run `terraform fmt` |
| PR Guardrails fail | Missing checklist | Complete PR template |
| Changelog policy fail | Missing entry | Create `docs/changelog/entries/CL-XXXX-*.md` |
| Session log required | Critical path change | Update session_capture + session_summary |

---

**Last Updated:** 2026-01-22
**Maintainer:** platform-team
