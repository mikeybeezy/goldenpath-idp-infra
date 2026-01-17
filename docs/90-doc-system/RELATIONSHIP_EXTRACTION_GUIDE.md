---
id: RELATIONSHIP_EXTRACTION_GUIDE
title: Relationship Extraction Guide
type: documentation
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - 12_GITOPS_AND_CICD
  - 21_CI_ENVIRONMENT_CONTRACT
  - ADR-0026-platform-cd-deployment-contract
  - ADR-0033-platform-ci-orchestrated-modes
  - ADR-0034-platform-ci-environment-contract
  - ADR-0047-platform-teardown-destroy-timeout-retry
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---
# Relationship Extraction Guide

## What It Does

The `extract-relationships.py` script automatically populates the `relates_to` metadata field by scanning document content for references to other files.

## How It Works

### Patterns Detected

1. **"Related:" field** (in doc contract section)

   ```markdown
   - Related: docs/adrs/ADR-0026.md, docs/40-delivery/12_GITOPS_AND_CICD.md
   ```

2. **Inline backtick references**

   ```markdown
   See `docs/adrs/ADR-0033-platform-ci-orchestrated-modes.md` for details.
   ```

3. **ADR mentions**

   ```markdown
   This relates to ADR-0047 and the teardown workflow.
   ```

4. **Markdown links**

   ```markdown
   See [CI Contract](../20-contracts/21_CI_ENVIRONMENT_CONTRACT.md)
   ```

5. **ci-workflows, apps, bootstrap references**

   ```markdown
   Workflow defined in `ci-workflows/CI_WORKFLOWS.md`
   ```

### ID Conversion

File paths are converted to document IDs:

- `docs/adrs/ADR-0026-platform-cd-deployment-contract.md` → `ADR-0026`
- `docs/40-delivery/12_GITOPS_AND_CICD.md` → `12_GITOPS_AND_CICD`
- `ci-workflows/CI_WORKFLOWS.md` → `CI_WORKFLOWS`

## Usage

### Step 1: Dry Run (Preview)

```bash
python3 scripts/extract-relationships.py --dry-run
```

Shows what would change without modifying files.

### Step 2: Run the Extraction

```bash
python3 scripts/extract-relationships.py
```

Updates `relates_to` fields in all markdown files with detected relationships.

### Step 3: Review Changes

```bash
git diff docs/ | grep "relates_to" -A 5
```

### Step 4: Commit

```bash
git add docs/ ci-workflows/ apps/ bootstrap/ modules/ gitops/ idp-tooling/
git commit -m "docs: populate document relationships for Knowledge Graph"
git push origin chore/metadata-backfill-batch-1
```

## Expected Results

### Before

```yaml
---
id: 21_CI_ENVIRONMENT_CONTRACT
title: CI Environment Contract
type: contract
relates_to: []
---

```

### After

```yaml
---
id: 21_CI_ENVIRONMENT_CONTRACT
title: CI Environment Contract
type: contract
relates_to:
  - 20_CI_ENVIRONMENT_SEPARATION
  - 17_BUILD_RUN_FLAGS
  - 25_PR_TERRAFORM_PLAN
  - ADR-0034
  - CI_WORKFLOWS
---
```

## Coverage

Based on analysis:

- **~160 files** will get auto-detected relationships (70%)
- **~50 files** will need manual curation (20%)
- **~26 files** already have relationships (10%)

## Troubleshooting

### If relationships aren't detected

Check that your documents have:

1. A "Related:" line in the doc contract
2. Inline references with backticks
3. Markdown links to other docs

### If wrong IDs are extracted

The script validates IDs against all docs in the repository. Invalid IDs are skipped with a warning in verbose mode.

### To see what was skipped

```bash
python3 scripts/extract-relationships.py --dry-run --verbose
```

## Integration with Knowledge Graph

These relationships enable:

1. **Graph traversal** - Navigate between related docs
2. **Impact analysis** - See what docs are affected by changes
3. **Orphan detection** - Find docs with no relationships
4. **Relationship types** - ADR → Implementation, Contract → Delivery, etc.

## Manual Refinement

After running the script, consider adding relationships for:

- Module READMEs → Related ADRs
- Templates → Documentation
- Indexes → All items they list
- Bi-directional links (ADR mentions Contract, Contract should mention ADR back)
