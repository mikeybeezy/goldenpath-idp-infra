---
id: pass-pr-gates
title: pass-pr-gates
type: documentation
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
schema_version: 1
relates_to: []
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
category: platform
status: active
version: '1.0'
description: Steps to ensure a Pull Request passes all repository-wide CI gates
supported_until: 2028-01-01
breaking_change: false
---

To ensure your Pull Request passes all CI gates (Metadata, Pre-commit, Super-Linter) in this repository, follow these steps before pushing:

### 1. Validate Metadata
Ensure all markdown files have the required frontmatter schema and that the `id` field matches the filename.
// turbo
```bash
python3 scripts/validate_metadata.py
```

### 2. Automated Formatting
Fix trailing whitespace, missing/extra newlines at EOF, and improperly formatted frontmatter markers.
// turbo
```bash
python3 scripts/format-docs.py
```

### 3. Local Linting
Run `markdownlint` to fix common style issues (lists, headings, horizontal rules) using the repository's configuration.
// turbo
```bash
markdownlint --fix .
```

### 4. Verify YAML & Whitespace
Run the pre-commit hooks locally if installed to catch any remaining issues.
```bash
pre-commit run --all-files
```

> [!TIP]
> If Super-Linter fails in CI but local checks pass, ensure that all long lines (>400 chars) are wrapped in `README.md` and that `.markdownlint.yml` is the only configuration file present in the root.
