---
id: METADATA_BACKFILL_SCRIPT
title: Metadata Backfill Script - Usage & Operations
type: runbook
category: unknown
version: '1.0'
owner: platform-team
status: active
dependencies:
- chart:redis
- module:aws_iam
- module:vpc
risk_profile:
  production_impact: high
  security_risk: access
  coupling_risk: high
reliability:
  rollback_strategy: not-applicable
  observability_tier: gold
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to:
- ADR-0084
- CL-0043
---

# Metadata Backfill Script - Usage & Operations

## Overview

`scripts/backfill-metadata.py` is an automated tool that adds YAML frontmatter metadata to all markdown files in the repository. It enables Knowledge Graph capabilities by ensuring 100% metadata coverage.

**Script Location:** [`scripts/backfill-metadata.py`](file:///Users/mikesablaze/goldenpath-idp-infra/scripts/backfill-metadata.py)

## What It Does

The script scans the entire repository for markdown files and adds comprehensive metadata including:

- **Core Identity:** id, title, type, category, version
- **Ownership:** owner, status
- **Dependencies:** module/chart/image references
- **Governance:** risk_profile, reliability, lifecycle
- **Relationships:** relates_to (empty array, populated by relationship script)

## How It Works

### 1. Discovery Phase

```python
# Finds all .md files excluding .gemini and node_modules
Scans: docs/, modules/, apps/, envs/, gitops/, bootstrap/, etc.
```

### 2. Analysis Phase

For each file:

- **Extracts title** from first `#` heading
- **Determines type** from directory (adr, changelog, contract, runbook, policy, documentation)
- **Extracts category** from directory structure (00-foundations, modules, apps, etc.)
- **Extracts version** from content (Helm charts, ArgoCD) or defaults to 1.0
- **Extracts dependencies** (Terraform modules, Helm charts, container images)

### 3. Generation Phase

Creates YAML frontmatter with:

- Quoted titles if they contain special characters (colons, brackets)
- Type-appropriate risk profiles and observability tiers
- Lifecycle dates based on document type
- Empty `relates_to` array (populated by extract-relationships.py)

### 4. Skip Logic

Skips files that already have `---` frontmatter (avoids duplicate metadata)

## Usage

### Quick Start

```bash
# Navigate to repository root
cd /Users/mikesablaze/goldenpath-idp-infra

# Run the script (updates files in-place)
python3 scripts/backfill-metadata.py
```

### Dry Run (Preview Mode)

```bash
# See what would change without modifying files
python3 scripts/backfill-metadata.py --dry-run

# Dry run with verbose output (shows skipped files)
python3 scripts/backfill-metadata.py --dry-run --verbose
```

### Output Example

```
Found 304 markdown files in repository
Mode: LIVE
============================================================
✅ modules/aws_eks/README.md
✅ apps/fast-api-app-template/README.md
✅ envs/dev/README.md
...
============================================================
✅ Updated: 206
⏭️  Skipped: 98
📊 Total: 304
```

## Generated Metadata Example

### Before (File without metadata)

```markdown
# AWS EKS Module

This module provisions an EKS cluster...
```

### After (With generated metadata)

```yaml
---
id: AWS_EKS_README
title: AWS EKS Module
type: documentation
category: modules
version: 1.0
owner: platform-team
status: active
dependencies:
  - module:vpc
  - module:aws_iam
risk_profile:
  production_impact: high
  security_risk: access
  coupling_risk: high
reliability:
  rollback_strategy: git-revert
  observability_tier: gold
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to: []
---

# AWS EKS Module

This module provisions an EKS cluster...
```

## Field Extraction Logic

### Category Detection

```
docs/00-foundations/file.md     → category: 00-foundations
docs/20-contracts/file.md       → category: 20-contracts
modules/aws_eks/README.md       → category: modules
apps/fast-api/README.md         → category: apps
```

### Version Extraction

```
Helm charts: Looks for "version: X.Y.Z" or "appVersion: X.Y.Z"
ArgoCD refs: Looks for "argocd version: X.Y.Z" patterns
Default: 1.0 for documentation
```

### Dependency Extraction

```
Terraform modules: Extracts module "name" references
Helm charts: Looks for chart dependency mentions
Apps: Extracts image: references (limited to 3)
```

### Type Detection

```
/adrs/ directory        → adr
/changelog/entries/     → changelog
/contracts/             → contract
/runbooks/              → runbook
/policies/ or security/ → policy
TEMPLATE in filename    → template
Default                 → documentation
```

## Validation

After running, validate all metadata:

```bash
python3 scripts/validate-metadata.py docs

# Expected output for success:
✅ Passed: 236
❌ Failed: 0
```

## Troubleshooting

### Issue: "Invalid YAML" errors

**Cause:** Title contains special characters (colons, brackets, quotes)

**Solution:** Script automatically quotes titles, but if errors persist:

```bash
# View the file
cat docs/path/to/file.md | head -20

# Manually quote the title field
title: "Your Title: With Colon"
```

### Issue: Wrong category assigned

**Cause:** File in unexpected directory

**Solution:**

1. Move file to correct directory, OR
2. Manually override category in frontmatter

### Issue: Dependencies not detected

**Cause:** Non-standard format in content

**Solution:** Manually add dependencies:

```yaml
dependencies:
  - module:vpc
  - chart:redis
  - image:python:3.11
```

### Issue: Version defaults to 1.0

**Cause:** No version pattern found in content

**Solution:** Manually set version in frontmatter:

```yaml
version: 5.46.7
```

## Integration with Other Tools

### 1. Relationship Extraction

Run after backfill to populate `relates_to`:

```bash
python3 scripts/backfill-metadata.py
python3 scripts/extract-relationships.py
```

### 2. Metadata Validation (CI)

Automatically validates metadata in CI:

```yaml
# .github/workflows/metadata-validation.yml
- name: Validate Metadata
  run: python3 scripts/validate-metadata.py docs
```

### 3. Knowledge Graph Import

Metadata enables import to graph databases:

```bash
# Future: Export to Neo4j/ArangoDB
python3 scripts/export-to-graph.py
```

## Maintenance

### Adding New Document Types

Edit `determine_doc_type()` function:

```python
def determine_doc_type(filepath):
    if '/new-type/' in filepath:
        return 'new-type'
    # ... existing logic
```

### Adding New Dependency Patterns

Edit `extract_dependencies()` function:

```python
def extract_dependencies(filepath):
    # Add new pattern
    new_deps = re.findall(r'new-pattern', content)
    dependencies.extend([f'prefix:{dep}' for dep in new_deps])
```

### Updating Risk Profiles

Edit `get_risk_profile()` function to adjust defaults per type.

## Script Arguments

| Argument | Description | Example |
|-------|-------|------|
| `--dry-run` | Preview mode, no file changes | `python3 ... --dry-run` |
| `--verbose` | Show skipped files | `python3 ... --verbose` |

## Best Practices

1. **Always run dry-run first** to preview changes
2. **Validate after running** with validate-metadata.py
3. **Commit changes incrementally** if running on large repos
4. **Review auto-generated dependencies** for accuracy
5. **Run on new files** when adding documentation

## Files Created/Modified

- Modifies: All `.md` files without frontmatter
- Creates: No new files (only adds frontmatter)
- Preserves: Original content below frontmatter

## Performance

- Processes ~300 files in <5 seconds
- Safe to re-run (skips files with metadata)
- No external dependencies (uses stdlib only)

## Related Documentation

- [ADR-0084: Enhanced Metadata Schema](file:///Users/mikesablaze/goldenpath-idp-infra/docs/adrs/ADR-0084-platform-enhanced-metadata-schema.md)
- [CL-0043: Complete Metadata Backfill](file:///Users/mikesablaze/goldenpath-idp-infra/docs/changelog/entries/CL-0043-complete-metadata-backfill.md)
- [METADATA_STRATEGY.md](file:///Users/mikesablaze/goldenpath-idp-infra/docs/90-doc-system/METADATA_STRATEGY.md)
- [Relationship Extraction Script Runbook](file:///Users/mikesablaze/goldenpath-idp-infra/docs/runbooks/RELATIONSHIP_EXTRACTION_SCRIPT.md)

## Support

For issues or questions:

1. Check troubleshooting section above
2. Review ADR-0084 for schema details
3. Contact platform-team
