<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: OB-0001-developer-security-tooling
title: Developer Security Tooling Onboarding
type: onboarding
relates_to:
  - ADR-0170
  - session-2026-01-19-build-pipeline-architecture
effective_date: 2026-01-19
related_govs:
  - GOV-0012
  - GOV-0013
---

# OB-0001: Developer Security Tooling Onboarding

## Purpose

Step-by-step guide for developers to set up required security tooling on their local development environment.

---

## Quick Start Checklist

### Mandatory (MUST complete before first PR)

- [ ] Install pre-commit framework
- [ ] Install and configure Gitleaks pre-commit hook
- [ ] Verify pre-commit hooks are active

### Recommended (SHOULD complete within first week)

- [ ] Install Snyk IDE extension
- [ ] Install Docker Scout (if using Docker Desktop)
- [ ] Configure IDE linting rules

---

## 1. Pre-commit Framework Setup

### 1.1 Install pre-commit

```bash
# macOS
brew install pre-commit

# pip (all platforms)
pip install pre-commit

# Verify installation
pre-commit --version
```

### 1.2 Initialize in Repository

```bash
# Navigate to your repo
cd your-app-repo

# Install hooks (reads .pre-commit-config.yaml)
pre-commit install

# Verify hooks are installed
pre-commit run --all-files
```

### 1.3 Required .pre-commit-config.yaml

If your repository doesn't have this file, create it:

```yaml
# .pre-commit-config.yaml
repos:
  # Secret detection - MANDATORY
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks

  # General checks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-merge-conflict
      - id: detect-private-key
      - id: trailing-whitespace
      - id: end-of-file-fixer

  # Python (if applicable)
  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black

  # YAML linting
  - repo: https://github.com/adrienverge/yamllint
    rev: v1.33.0
    hooks:
      - id: yamllint
        args: ['-d', '{extends: relaxed, rules: {line-length: {max: 120}}}']
```

---

## 2. Gitleaks Setup

### 2.1 Verify Gitleaks Works

```bash
# Run gitleaks manually
gitleaks detect --source . --verbose

# Expected output (clean repo):
# INFO[0000] 0 commits scanned.
# INFO[0000] no leaks found
```

### 2.2 Test Secret Detection

Create a test file to verify detection works:

```bash
# Create test secret (DO NOT COMMIT)
echo 'aws_secret_access_key = "AKIAIOSFODNN7EXAMPLE"' > test-secret.txt

# Run gitleaks
gitleaks detect --source . --verbose

# Should detect the secret
# Delete the test file
rm test-secret.txt
```

### 2.3 Allowlist Configuration

If you have false positives, create `.gitleaks.toml`:

```toml
# .gitleaks.toml
[allowlist]
paths = [
    '''\.gitleaks\.toml$''',
    '''test/fixtures/.*''',
]

# Allow specific patterns (be careful!)
regexes = [
    '''EXAMPLE.*''',
]
```

---

## 3. IDE Extensions

### 3.1 VS Code

| Extension | Purpose | Required |
|-----------|---------|----------|
| **Snyk Security** | SCA + SAST scanning | Recommended |
| Docker | Container management | Recommended |
| GitLens | Git history + blame | Recommended |
| YAML | YAML validation | Recommended |
| ESLint/Pylint | Language linting | Per language |

**Install Snyk:**
1. Open VS Code Extensions (Cmd+Shift+X)
2. Search "Snyk Security"
3. Click Install
4. Authenticate with Snyk account (free tier available)

### 3.2 JetBrains (IntelliJ, PyCharm, GoLand)

| Plugin | Purpose | Required |
|--------|---------|----------|
| **Snyk** | SCA + SAST scanning | Recommended |
| Docker | Container management | Recommended |
| SonarLint | Code quality + security | Recommended |

**Install Snyk:**
1. Open Settings > Plugins
2. Search "Snyk"
3. Click Install
4. Restart IDE
5. Authenticate via Settings > Tools > Snyk

---

## 4. Docker Scout Setup

### 4.1 Enable in Docker Desktop

1. Open Docker Desktop
2. Go to Settings > Features in Development
3. Enable "Docker Scout"
4. Apply & Restart

### 4.2 CLI Usage

```bash
# Scan local image for CVEs
docker scout cves myapp:latest

# Quick overview
docker scout quickview myapp:latest

# Generate SBOM
docker scout sbom --format spdx-json myapp:latest > sbom.json

# Compare images
docker scout compare myapp:v1 myapp:v2
```

### 4.3 Recommended Workflow

Before pushing an image:

```bash
# Build image
docker build -t myapp:dev .

# Quick scan
docker scout quickview myapp:dev

# If issues found, investigate
docker scout cves myapp:dev

# Fix issues, rebuild, rescan
```

---

## 5. Local Testing Commands

### 5.1 Run All Security Checks

```bash
# Run all pre-commit hooks
pre-commit run --all-files

# Run specific hook
pre-commit run gitleaks --all-files
```

### 5.2 Scan Dependencies

```bash
# Snyk CLI (if installed)
snyk test

# npm audit (Node.js)
npm audit

# pip-audit (Python)
pip-audit

# govulncheck (Go)
govulncheck ./...
```

### 5.3 Scan Docker Image

```bash
# Trivy (recommended)
trivy image myapp:latest

# Docker Scout
docker scout cves myapp:latest

# Both produce similar results - use one consistently
```

---

## 6. Troubleshooting

### 6.1 Pre-commit Not Running

```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install

# Clear cache
pre-commit clean

# Update hooks
pre-commit autoupdate
```

### 6.2 Gitleaks False Positives

Add to `.gitleaks.toml`:

```toml
[[rules]]
id = "custom-allowlist"
description = "Allow test fixtures"
path = '''test/.*'''
```

Or use inline comments:

```yaml
# gitleaks:allow
api_key: "test-key-not-real"
```

### 6.3 Snyk Authentication Issues

```bash
# Re-authenticate
snyk auth

# Check status
snyk config get api

# Use token directly
export SNYK_TOKEN=your-token
```

---

## 7. Verification

### 7.1 Self-Check

Run this to verify your setup:

```bash
#!/bin/bash
echo "=== Security Tooling Verification ==="

echo -n "pre-commit: "
pre-commit --version 2>/dev/null && echo "OK" || echo "MISSING"

echo -n "gitleaks: "
gitleaks version 2>/dev/null && echo "OK" || echo "MISSING"

echo -n "hooks installed: "
[ -f .git/hooks/pre-commit ] && echo "OK" || echo "MISSING"

echo -n "trivy: "
trivy --version 2>/dev/null && echo "OK" || echo "OPTIONAL"

echo -n "snyk: "
snyk --version 2>/dev/null && echo "OK" || echo "OPTIONAL"

echo "=== Complete ==="
```

### 7.2 Test Commit

```bash
# Stage a file
git add somefile.txt

# Commit (hooks should run)
git commit -m "test: verify pre-commit hooks"

# If hooks pass, you're good!
```

---

## 8. Getting Help

| Issue | Contact |
|-------|---------|
| Pre-commit setup | #platform-support |
| Snyk licensing | #security-team |
| False positives | File issue in goldenpath-idp-infra |
| New tool requests | ADR required, discuss with platform-team |

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-01-19 | Initial version | platform-team |

---

## Related Documents

- GOV-0012: Build Pipeline Standards
- GOV-0013: DevSecOps Security Standards
- ADR-0170: Build Pipeline Architecture

Signed: platform-team (2026-01-19)
