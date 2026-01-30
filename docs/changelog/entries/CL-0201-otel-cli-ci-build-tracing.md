---
id: CL-0201-otel-cli-ci-build-tracing
title: OpenTelemetry CLI Integration for CI Build Tracing
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to:
  - ci-cd
  - observability
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
  maturity: 2
schema_version: 1
relates_to:
  - ADR-0055-platform-tempo-tracing-backend
  - ADR-0054-platform-observability-exporters-otel-split
  - HELM_TEMPO
  - CL-0200-backstage-branch-protection-governance
supersedes: []
superseded_by: []
tags:
  - ci-cd
  - opentelemetry
  - observability
  - tracing
inheritance: {}
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# CL-0201: OpenTelemetry CLI Integration for CI Build Tracing

## Summary

Implemented OpenTelemetry CLI (otel-cli) integration in the Backstage CI workflow to enable distributed tracing for build pipelines. This moves the "CI Build Tracing" capability from **Planned** to **Implemented** in the V1 capability matrix.

## Problem

CI pipelines lacked observability into build performance and timing. Without tracing:

- No visibility into which stages are slow
- No correlation between CI runs and deployed artifacts
- No metrics for build duration trends
- No integration with the existing Tempo tracing backend

## Solution

Added otel-cli instrumentation to the Backstage CI workflow (`goldenpath-idp-backstage/.github/workflows/ci.yml`):

### New Jobs/Steps

| Component | Purpose |
|-----------|---------|
| `setup-otel` job | Initializes otel-cli and sends pipeline start span |
| Build step tracing | Wraps `yarn build:backend` with `otel-cli exec` |
| Docker tracing | Sends spans before/after Docker build & push |
| Summary tracing | Sends pipeline complete span with all job results |

### Configuration

```yaml
env:
  OTEL_EXPORTER_OTLP_ENDPOINT: ${{ vars.OTEL_EXPORTER_OTLP_ENDPOINT || 'https://tempo.goldenpath.dev' }}
  OTEL_SERVICE_NAME: 'backstage-ci'
  OTEL_CLI_VERSION: '0.4.5'
```

### Traced Operations

| Span Name | Attributes | When |
|-----------|------------|------|
| `ci-pipeline-start` | run_id, actor, ref, sha | Pipeline begins |
| `yarn-build-backend` | run_id, build.tag | During backend build |
| `docker-build-push-start` | run_id, image.tag, platforms | Before Docker build |
| `docker-build-push-complete` | run_id, image.tag, status | After Docker push |
| `ci-pipeline-complete` | run_id, lint/test/build/security results | Pipeline ends |

### Graceful Degradation

If `OTEL_EXPORTER_OTLP_ENDPOINT` is not configured:

- otel-cli commands silently succeed (no traces sent)
- Build continues normally without observability
- No CI failures due to missing endpoint

## Implementation Details

### otel-cli Installation

Each job that needs tracing installs otel-cli:

```bash
curl -sLO "https://github.com/equinix-labs/otel-cli/releases/download/v0.4.5/otel-cli_0.4.5_linux_amd64.tar.gz"
tar xzf "otel-cli_0.4.5_linux_amd64.tar.gz"
sudo mv otel-cli /usr/local/bin/
```

### Traced Build Example

```bash
otel-cli exec \
  --service "backstage-ci" \
  --name "yarn-build-backend" \
  --attrs "github.run_id=${{ github.run_id }},build.tag=${{ steps.tag.outputs.tag }}" \
  -- yarn build:backend
```

### Span-Only Example (for GitHub Actions)

For steps using GitHub Actions (like docker/build-push-action), we send discrete spans:

```bash
otel-cli span \
  --service "backstage-ci" \
  --name "docker-build-push-complete" \
  --attrs "status=success"
```

## Files Changed

- `goldenpath-idp-backstage/.github/workflows/ci.yml`
  - Added `setup-otel` job
  - Added otel-cli installation to `build`, `docker`, and `summary` jobs
  - Wrapped build steps with `otel-cli exec`
  - Added span markers for Docker build/push

## Activation

To enable tracing, set the repository variable:

```bash
gh variable set OTEL_EXPORTER_OTLP_ENDPOINT \
  --body "https://tempo.goldenpath.dev" \
  --repo mikeybeezy/goldenpath-idp-backstage
```

## Validation

After activation, verify traces in Grafana:

1. Navigate to Grafana → Explore → Tempo
2. Search for service: `backstage-ci`
3. Filter by `github.run_id` attribute
4. View trace waterfall showing pipeline stages

## Impact

- **Observability:** CI builds now visible in Tempo
- **Performance:** Can identify slow stages via trace durations
- **Correlation:** Build traces linked to run IDs and image tags
- **Cost:** Minimal (otel-cli is lightweight, ~5s per job for install)

## V1 Capability Matrix Update

| Capability | Before | After |
|------------|--------|-------|
| CI Build Tracing | ⚠️ Planned | ✅ Implemented |

## Related

- [ADR-0055](../../docs/adrs/ADR-0055-platform-tempo-tracing-backend.md) - Tempo as tracing backend
- [Tempo README](../../gitops/helm/tempo/README.md) - otel-cli usage documentation
- [CL-0200](./CL-0200-backstage-branch-protection-governance.md) - Branch governance (same session)
