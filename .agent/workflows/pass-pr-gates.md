---
description: Steps to ensure a Pull Request passes all repository-wide CI gates
---

To ensure your Pull Request passes all CI gates (Metadata, Pre-commit, Super-Linter) in this repository, follow these steps before pushing:

### 1. Validate Metadata
Ensure all markdown files have the required frontmatter schema and that the `id` field matches the filename.
// turbo
```bash
python3 scripts/validate-metadata.py
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
