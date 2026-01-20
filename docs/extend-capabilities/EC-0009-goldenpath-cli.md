---
id: EC-0009-goldenpath-cli
title: GoldenPath Platform CLI
type: extension-capability
status: proposed
owner: platform-team
domain: platform-core
relates_to:
  - ADR-0167
  - EC-0008-session-capture-ui
  - EC-0010-agent-pairing-mode
  - RB-0033-persistent-cluster-teardown
  - SCRIPT_CERTIFICATION_MATRIX
priority: medium
vq_class: 🔴 HV/HQ
estimated_roi: $15K/year
effort_estimate: 1-3 days (shell wrapper) to 1 week (full CLI)
---
## Executive Summary

A unified command-line interface (`gp`) for GoldenPath IDP that wraps existing scripts, Makefile targets, bootstrap sequences, and troubleshooting workflows. Designed for **platform team operations first**, with developer self-service as a secondary concern.

**Key Benefits**:
- Single entry point for all platform operations
- Discoverability via `gp --help` instead of memorizing paths
- Guided workflows for complex multi-step operations
- IAM role segregation for privileged operations
- Reduced cognitive load during incident response

**Estimated ROI**: $15K/year from faster troubleshooting, reduced onboarding friction, and fewer "how do I run X?" interruptions.

## Problem Statement

### Current State

```text
Platform Operations Today:
├── python3 scripts/scaffold_ecr.py --app foo
├── python3 scripts/validate_metadata.py docs/
├── python3 scripts/rds_request_parser.py ...
├── make rds-provision ENV=dev
├── ./bootstrap/10_bootstrap/goldenpath-idp-bootstrap-v3.sh
├── ./bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v3.sh
└── ... 40+ scripts, 20+ make targets, 10+ bootstrap scripts
```

### Pain Points

1. **Discovery Friction**: New team members don't know what scripts exist
2. **Inconsistent Interfaces**: Some scripts need `python3`, some are bash, some are Make
3. **Complex Sequences**: Bootstrap/teardown require running multiple scripts in order
4. **No Guided Flows**: Self-service requests need manual file creation + workflow dispatch
5. **Privilege Confusion**: Unclear which operations need elevated permissions

### Target Audiences

| Audience | Primary Use Cases | Priority |
|----------|-------------------|----------|
| **Platform Team** | Bootstrap, teardown, diagnose, audit | **P0** |
| **SRE/Ops** | Runbook execution, health checks, incident response | **P1** |
| **Developers** | Scaffold, request, validate | P2 |

## Proposed Solution

### Command Structure

```bash
gp <domain> <action> [options]

# Platform Operations (privileged)
gp bootstrap cluster --env dev --build-id 20-01-26-01
gp teardown cluster --env dev --build-id 20-01-26-01
gp provision rds --env dev
gp diagnose cluster --env dev

# Self-Service Requests
gp request ecr --app hello-world
gp request s3 --app hello-world --bucket data
gp request rds --app hello-world --database mydb

# Governance & Validation
gp validate metadata docs/
gp validate enums
gp audit scripts
gp health

# Documentation & Discovery
gp runbook list
gp runbook show RB-0033
gp docs search "teardown"
```

### Implementation Tiers

#### Tier 1: Shell Wrapper (1-3 days)

Simple bash dispatcher that routes to existing tools:

```bash
#!/bin/bash
# bin/gp - GoldenPath CLI wrapper

set -euo pipefail

SCRIPTS_DIR="$(dirname "$0")/../scripts"
BOOTSTRAP_DIR="$(dirname "$0")/../bootstrap"

case "${1:-help}" in
  # Self-service
  request)
    case "$2" in
      ecr) shift 2; python3 "$SCRIPTS_DIR/scaffold_ecr.py" "$@" ;;
      s3)  shift 2; python3 "$SCRIPTS_DIR/s3_request_parser.py" "$@" ;;
      rds) shift 2; python3 "$SCRIPTS_DIR/rds_request_parser.py" "$@" ;;
      eks) shift 2; python3 "$SCRIPTS_DIR/eks_request_parser.py" "$@" ;;
      *)   echo "Usage: gp request {ecr|s3|rds|eks} [options]" ;;
    esac ;;

  # Validation
  validate)
    case "$2" in
      metadata) shift 2; python3 "$SCRIPTS_DIR/validate_metadata.py" "$@" ;;
      enums)    python3 "$SCRIPTS_DIR/validate_enums.py" ;;
      *)        echo "Usage: gp validate {metadata|enums} [path]" ;;
    esac ;;

  # Platform operations (privileged)
  bootstrap)
    case "$2" in
      cluster) shift 2; "$BOOTSTRAP_DIR/10_bootstrap/goldenpath-idp-bootstrap-v3.sh" "$@" ;;
      *)       echo "Usage: gp bootstrap {cluster} [options]" ;;
    esac ;;

  teardown)
    case "$2" in
      cluster) shift 2; "$BOOTSTRAP_DIR/60_tear_down_clean_up/goldenpath-idp-teardown-v3.sh" "$@" ;;
      *)       echo "Usage: gp teardown {cluster} [options]" ;;
    esac ;;

  # Observability
  health) python3 "$SCRIPTS_DIR/platform_health.py" "$@" ;;
  audit)  python3 "$SCRIPTS_DIR/audit_metadata.py" "$@" ;;

  # Documentation
  runbook)
    case "$2" in
      list) ls -1 docs/70-operations/runbooks/RB-*.md | xargs -I{} basename {} .md ;;
      show) cat "docs/70-operations/runbooks/$3.md" 2>/dev/null || echo "Runbook not found: $3" ;;
      *)    echo "Usage: gp runbook {list|show <id>}" ;;
    esac ;;

  help|--help|-h)
    cat <<EOF
GoldenPath Platform CLI

Usage: gp <command> [subcommand] [options]

Commands:
  request     Self-service resource requests (ecr, s3, rds, eks)
  validate    Run validation scripts (metadata, enums)
  bootstrap   Platform bootstrap operations (cluster)
  teardown    Platform teardown operations (cluster)
  provision   Provision resources (rds)
  health      Platform health check
  audit       Audit metadata and scripts
  runbook     Browse runbooks (list, show)
  diagnose    Troubleshooting workflows

Run 'gp <command> --help' for command-specific help.
EOF
    ;;

  *) echo "Unknown command: $1. Run 'gp help' for usage." ;;
esac
```

#### Tier 2: Python Click CLI (1 week)

Full CLI with:
- Proper argument parsing and validation
- Interactive prompts for missing required args
- Shell completion
- Colored output
- Progress indicators for long operations

```python
# bin/gp (Python entry point)
import click

@click.group()
def cli():
    """GoldenPath Platform CLI"""
    pass

@cli.group()
def request():
    """Self-service resource requests"""
    pass

@request.command()
@click.option('--app', required=True, help='Application name')
@click.option('--dry-run', is_flag=True, help='Show what would be created')
def ecr(app, dry_run):
    """Request an ECR repository"""
    # Calls scaffold_ecr.py with proper args
    pass

# ... more commands
```

#### Tier 3: Plugin Architecture (Future)

Extensible framework allowing teams to add custom commands without modifying core CLI.

### IAM Role Segregation

```yaml
# Proposed permission tiers
gp_developer:
  - request/*
  - validate/*
  - runbook/*
  - health (read-only)

gp_operator:
  - all of gp_developer
  - diagnose/*
  - audit/*

gp_platform:
  - all of gp_operator
  - bootstrap/*
  - teardown/*
  - provision/*
```

## Implementation Path

### Phase 1: Shell Wrapper (P2 - Q1)

1. Create `bin/gp` shell wrapper
2. Add to PATH via Makefile or install script
3. Document basic usage in README
4. Test with common workflows

### Phase 2: Enhanced CLI (P3 - Q2)

1. Migrate to Python Click if shell limits reached
2. Add interactive prompts
3. Add shell completion
4. Integrate with CI for validation

### Phase 3: IAM Integration (P4 - Q2+)

1. Design permission model
2. Implement role checks
3. Add audit logging for privileged operations

## Success Criteria

| Metric | Target |
|--------|--------|
| Command discoverability | `gp --help` covers 80% of common operations |
| Onboarding time | New team member productive in < 1 hour |
| Incident response | Runbook lookup < 10 seconds |
| Adoption | Used by 100% of platform team within 1 month |

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Maintenance overhead | Medium | Start with thin wrapper, only add complexity when needed |
| Out-of-sync with scripts | Medium | CLI calls scripts directly, doesn't duplicate logic |
| Scope creep | High | Strict phased approach, defer IAM until proven need |
| Adoption resistance | Low | CLI wraps existing tools, doesn't replace them |

## Decision

**Status**: Proposed (P2 - defer to Q2)

**Rationale**: Higher value than Session UI (EC-0008) due to operational impact, but should wait until:
1. Bootstrap/teardown flows are stable
2. Request parsers are battle-tested
3. Repeated friction observed with current approach

**Trigger to build**: When platform team repeatedly writes wrapper scripts or documents "run these 5 commands in order" patterns.

---

## References

- [Script Certification Matrix](../10-governance/SCRIPT_CERTIFICATION_MATRIX.md)
- [Makefile](../../Makefile)
- [Bootstrap Scripts](../../bootstrap/)
- [Platform Health Script](../../scripts/platform_health.py)

Signed: platform-team (2026-01-20)
