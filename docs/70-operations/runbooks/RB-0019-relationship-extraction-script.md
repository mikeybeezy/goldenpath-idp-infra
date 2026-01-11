---
id: RB-0019-relationship-extraction-script
title: Relationship Extraction Script - Usage & Operations
type: runbook
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: high
  security_risk: access
  coupling_risk: high
reliability:
  rollback_strategy: rerun-teardown
  observability_tier: gold
schema_version: 1
relates_to:
  - 21_CI_ENVIRONMENT_CONTRACT
  - ADR-0026
  - ADR-0030
  - ADR-0032
  - ADR-0033
  - ADR-0033-platform-ci-orchestrated-modes
  - ADR-0034
  - ADR-0047
  - ADR-0056
  - ADR-0067
  - ADR-0084
  - CL-0016
  - CL-0042
  - CL-0043
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
category: runbooks
status: active
version: '1.0'
dependencies: []
supported_until: 2028-01-01
breaking_change: false
---

# Relationship Extraction Script - Usage & Operations

## Overview

`scripts/extract-relationships.py` automatically populates the `relates_to` metadata field by scanning document content for references to other files, ADRs, PRs, and workflow files. It builds the Knowledge Graph connections between documents.

**Script Location:** [`scripts/extract-relationships.py`](scripts/extract-relationships.py)

## What It Does

The script detects 13 relationship patterns in markdown content and populates `relates_to` arrays with:

- Document IDs (ADR-0026, CL-0042, 21_CI_ENVIRONMENT_CONTRACT)
- PR references (PR-107, PR-126)
- GitHub workflow files (workflow:pr-labeler, workflow:terraform-plan)

## How It Works

### 1. Document Index Phase

```python
# Builds index of all document IDs in repository
Scans: 304 markdown files
Creates: ID mapping (file path → document ID)
```

### 2. Content Analysis Phase

For each file, extracts references using **13 detection patterns**:

1. **"Related:" field** in doc contract
2. **Inline backtick** references
3. **ADR mentions** (`ADR-0047`)
4. **Markdown links** (`[text](path.md)`)
5. **ci-workflows/** files
6. **apps/** references
7. **Changelog mentions** (`CL-0042`)
8. **Policies/** references
9. **Governance/** references
10. **Contracts/** references
11. **Runbooks/** references
12. **PR references** (`PR #107`)
13. **GitHub workflows** (`.github/workflows/file.yml`)

### 3. ID Conversion Phase

Converts file paths to document IDs:

```
docs/adrs/ADR-0026-platform-cd-deployment.md → ADR-0026
docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md → 21_CI_ENVIRONMENT_CONTRACT
PR #107 → PR-107
.github/workflows/pr-labeler.yml → workflow:pr-labeler
```

### 4. Validation Phase

- Checks if referenced IDs exist in repository index
- Skips self-references
- Removes duplicates

### 5. Update Phase

- Merges with existing `relates_to` array
- Sorts alphabetically
- Skips if no changes detected

## Usage

### Quick Start

```bash
# Navigate to repository root
cd /Users/mikesablaze/goldenpath-idp-infra

# Run the script (updates relates_to fields in-place)
python3 scripts/extract-relationships.py
```

### Dry Run (Preview Mode)

```bash
# See what relationships would be added without modifying files
python3 scripts/extract-relationships.py --dry-run

# Dry run with verbose output (shows skipped files)
python3 scripts/extract-relationships.py --dry-run --verbose
```

### Output Example

```
Found 304 markdown files
Indexed 304 document IDs
Mode: LIVE
============================================================
✅ docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md
   Added 5 relationships: ['17_BUILD_RUN_FLAGS', '20_CI_ENVIRONMENT_SEPARATION', ...]
✅ docs/adrs/ADR-0067-platform-labeler-base-ref.md
   Added 2 relationships: ['CL-0016', 'PR-107', 'workflow:pr-labeler']
...
============================================================
✅ Updated: 160
  Skipped: 144
 Total: 304
```

## Detection Pattern Examples

### Pattern 1: "Related:" Field

```markdown
- Related: docs/adrs/ADR-0026.md, docs/40-delivery/12_GITOPS.md
```

**Extracts:** `ADR-0026`, `12_GITOPS_AND_CICD`

### Pattern 2: Inline Backtick References

```markdown
See `docs/adrs/ADR-0033-platform-ci-orchestrated-modes.md` for details.
```

**Extracts:** `ADR-0033`

### Pattern 3: ADR Mentions

```markdown
This relates to ADR-0047 and the teardown workflow.
```

**Extracts:** `ADR-0047`

### Pattern 4: Markdown Links

```markdown
[CI Contract](../20-contracts/21_CI_ENVIRONMENT_CONTRACT.md)
```

**Extracts:** `21_CI_ENVIRONMENT_CONTRACT`

### Pattern 7: Changelog Mentions

```markdown
Related: CL-0042 and CL-0043
```

**Extracts:** `CL-0042`, `CL-0043`

### Pattern 12: PR References

```markdown
Related: PR #107, PR #126
```

**Extracts:** `PR-107`, `PR-126`

### Pattern 13: GitHub Workflows

```markdown
Workflow: `.github/workflows/pr-labeler.yml`
```

**Extracts:** `workflow:pr-labeler`

## Metadata Transformation

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
  - 17_BUILD_RUN_FLAGS
  - 20_CI_ENVIRONMENT_SEPARATION
  - 25_PR_TERRAFORM_PLAN
  - 33_IAM_ROLES_AND_POLICIES
  - ADR-0030
  - ADR-0033
  - ADR-0034
  - CI_WORKFLOWS
---
```

## Validation

After running, verify relationships are valid:

```bash
# Validate metadata (checks for broken references)
python3 scripts/validate_metadata.py docs

# View relationship count per file
grep -r "relates_to:" docs/ | wc -l

# Find files with no relationships
grep -r "relates_to: \[\]" docs/ | wc -l
```

## Troubleshooting

### Issue: Relationships not detected

**Cause:** Document doesn't use standard reference patterns

**Solution:** Add explicit references:

```markdown
- Related: docs/adrs/ADR-0026.md, docs/70-operations/runbooks/05_GOLDEN_PATH.md
```

### Issue: Invalid IDs extracted

**Cause:** Referenced file doesn't exist or ID conversion failed

**Check verbose mode:**

```bash
python3 scripts/extract-relationships.py --dry-run --verbose
```

**Solution:** Ensure referenced files exist, or manually add to `relates_to`

### Issue: Self-references added

**Cause:** Bug in skip logic (should auto-filter)

**Solution:** Manually remove from `relates_to` array

### Issue: Duplicate relationships

**Cause:** Multiple patterns detected same relationship

**Solution:** Script auto-deduplicates, but verify with:

```bash
# Check for duplicates in a file
yq '.relates_to | unique' docs/path/to/file.md
```

## Expected Coverage

Based on repository analysis:

- **High Coverage (80-100%):** Contracts, ADRs with cross-refs, runbooks
- **Medium Coverage (50-80%):** Changelogs with PR refs, delivery docs
- **Low Coverage (20-50%):** Module READMEs, app templates, bootstrap docs
- **Manual Curation Needed:** ~30% of files (implicit relationships)

## Integration Workflow

### Standard Workflow

```bash
# 1. Run backfill first (adds metadata structure)
python3 scripts/backfill-metadata.py

# 2. Run relationship extraction (populates relates_to)
python3 scripts/extract-relationships.py

# 3. Validate
python3 scripts/validate_metadata.py docs

# 4. Commit
git add docs/
git commit -m "docs: populate document relationships"
```

### Incremental Updates

```bash
# Re-run after adding new cross-references
python3 scripts/extract-relationships.py

# Only updates files with new/changed relationships
```

## Manual Relationship Curation

For the ~30% not auto-detected, manually add:

```yaml
relates_to:
  - ADR-0032  # Manual: EKS architecture decision
  - ADR-0056  # Manual: EKS access model
  - 31_EKS_ACCESS_MODEL  # Manual: Implementation doc
```

**Bi-directional links:** If ADR-0026 mentions Contract 29, ensure Contract 29 mentions ADR-0026 back.

## Performance

- Processes ~300 files in <10 seconds
- Safe to re-run (only updates changed relationships)
- Memory-efficient (processes files stream)

## Script Arguments

| Argument | Description | Example |
|-------|-------|------|
| `--dry-run` | Preview mode, no file changes | `python3 ... --dry-run` |
| `--verbose` | Show all files including skipped | `python3 ... --verbose` |

## Advanced Usage

### Finding Orphaned Documents

```bash
# Find docs with no relationships
python3 scripts/extract-relationships.py
grep -r "relates_to: \[\]" docs/
```

### Relationship Density Analysis

```python
# Count relationships per file
import yaml, glob
for f in glob.glob('docs/**/*.md', recursive=True):
    with open(f) as file:
        meta = yaml.safe_load(file.read().split('---')[1])
        print(f"{f}: {len(meta.get('relates_to', []))} relationships")
```

### Exporting Relationship Graph

```bash
# Future: Export to graph format
python3 scripts/export-relationships-graph.py --format graphml
```

## Maintenance

### Adding New Patterns

Edit `extract_relationships_from_content()` function:

```python
# Pattern 14: My new pattern
new_pattern = re.findall(r'my-pattern-regex', content)
relationships.update(new_pattern)
```

### Adjusting ID Conversion

Edit `extract_doc_id_from_path()` function for custom ID formats.

### Excluding Certain References

Add filter logic before adding to `relationships` set.

## Known Limitations

1. **Cannot detect semantic relationships** (requires AI/manual)
2. **Relative path resolution** may fail for complex directory structures
3. **PR references** only work for numeric PRs (e.g., `PR #107`)
4. **Workflow files** must be in `.github/workflows/` directory

## Best Practices

1. **Use "Related:" field** in doc contract for explicit relationships
2. **Use backtick refs** for inline references
3. **Mention ADRs/CLs** by ID in content
4. **Re-run after major refactors** to update relationships
5. **Manually curate high-value** documents (architecture, contracts)

## Related Documentation

- [ADR-0084: Enhanced Metadata Schema](docs/adrs/ADR-0084-platform-enhanced-metadata-schema.md)
- [CL-0043: Complete Metadata Backfill](docs/changelog/entries/CL-0043-complete-metadata-backfill.md)
- [METADATA_STRATEGY.md](docs/90-doc-system/METADATA_STRATEGY.md)
- [Metadata Backfill Script Runbook](docs/70-operations/runbooks/METADATA_BACKFILL_SCRIPT.md)

## Support

For issues or questions:

1. Check troubleshooting section above
2. Review the 13 detection patterns
3. Inspect verbose output for debugging
4. Contact platform-team
