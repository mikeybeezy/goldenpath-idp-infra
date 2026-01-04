---
id: METADATA_BACKFILL_INSTRUCTIONS
title: Metadata Backfill Instructions
type: documentation
owner: platform-team
status: active
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to: []
---

# Metadata Backfill Instructions

## Quick Start

```bash
# 1. Review what will be changed (dry run)
python3 scripts/backfill-metadata.py --dry-run --verbose

# 2. Apply the metadata backfill
python3 scripts/backfill-metadata.py

# 3. Validate the metadata
python3 scripts/validate-metadata.py docs

# 4. Review the changes
git diff docs/

# 5. Commit if everything looks good
git add docs/
git commit -m "docs: complete metadata backfill for all remaining files"
git push origin chore/metadata-backfill-batch-1
```

## What the Script Does

The `backfill-metadata.py` script:

- ✅ Finds all markdown files in `docs/` without metadata
- ✅ Extracts the title from the first `#` heading
- ✅ Determines document type based on location (changelog, adr, contract, runbook, etc.)
- ✅ Generates appropriate `id` based on filename conventions
- ✅ Sets lifecycle dates (1 year for changelogs, 2 years for ADRs, 2028 for others)
- ✅ Assigns risk profiles based on document type
- ✅ Quotes titles with colons to avoid YAML parsing errors
- ✅ Adds complete YAML frontmatter to each file

## Expected Results

**Before running:**
- 75 files with metadata
- 161 files without metadata

**After running:**
- 236 files with metadata (100%)
- 0 files without metadata

## Current Progress

✅ **Already Completed:**
- Batch 1: 14 files (contracts, onboarding, changelog meta) - COMMITTED
- Build run logs: 6 files - COMMITTED
- PR #145 fixes: 40+ ADRs with quoted titles - COMMITTED

⏳ **Remaining:** ~161 files

## Safety Features

- **Dry run mode:** Use `--dry-run` to preview changes without modifying files
- **Skip existing:** Never overwrites files that already have metadata
- **Error handling:** Continues on errors, reports issues at the end
- **Verbose mode:** Use `--verbose` to see all files including skipped ones

## Troubleshooting

### If validation fails after backfill

Check for YAML syntax errors:
```bash
python3 scripts/validate-metadata.py docs 2>&1 | grep -A 3 "ERROR"
```

### If some titles need manual adjustment

Edit the files directly and re-validate:
```bash
# Fix the file
# Then validate
python3 scripts/validate-metadata.py docs/path/to/file.md
```

## Next Steps After Completion

1. ✅ All 236 files have metadata
2. Push changes to branch
3. Update walkthrough artifact
4. Merge PR #145 if not already merged
5. Consider backfilling infrastructure tags (HCL files) per METADATA_STRATEGY.md
