---
id: HELM_TEMPO
title: Tempo Helm Chart (Values)
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
  observability_tier: silver
  maturity: 1
schema_version: 1
relates_to:
  - ADR-0055-platform-tempo-tracing-backend
  - HELM_KUBE_PROMETHEUS_STACK
  - HELM_LOKI
supersedes: []
superseded_by: []
tags:
  - observability
  - tracing
  - opentelemetry
inheritance: {}
value_quantification:
  vq_class: LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
category: delivery
status: active
version: 1.0
dependencies:
  - chart:tempo
  - image:tempo
supported_until: 2028-01-01
breaking_change: false
---

# Tempo Helm Deployment

Grafana Tempo is the distributed tracing backend for the GoldenPath IDP platform.
It receives traces via OTLP (OpenTelemetry Protocol) and integrates with Grafana
for visualization.

## Architecture

```
                                    ┌─────────────────┐
                                    │   Grafana UI    │
                                    │  (query traces) │
                                    └────────┬────────┘
                                             │
┌──────────────┐    OTLP/gRPC      ┌─────────▼─────────┐
│  otel-cli    │──────────────────▶│      Tempo        │
│  (CI builds) │     :4317         │  (single binary)  │
└──────────────┘                   └───────────────────┘
                                             │
┌──────────────┐    OTLP/HTTP               │
│ App Services │──────────────────▶         │
│ (OTel SDK)   │     :4318                  │
└──────────────┘                   ┌────────▼────────┐
                                   │   S3 Storage    │
                                   │  (prod only)    │
                                   └─────────────────┘
```

## Directory Structure

```
gitops/helm/tempo/
├── README.md
├── metadata.yaml
└── values/
    ├── dev.yaml      # SingleBinary, local storage, 3d retention
    ├── test.yaml     # SingleBinary, local storage, 7d retention
    ├── staging.yaml  # SingleBinary, S3 storage, 14d retention
    └── prod.yaml     # Distributed, S3 storage, 30d retention
```

## Usage

Used by Argo CD Applications (`gitops/argocd/apps/<env>/tempo.yaml`) via:
```yaml
helm:
  valueFiles:
    - $values/gitops/helm/tempo/values/<env>.yaml
```

## Endpoints

| Protocol | Port | Path | Use Case |
|----------|------|------|----------|
| OTLP gRPC | 4317 | - | High-volume trace ingestion |
| OTLP HTTP | 4318 | /v1/traces | Simple HTTP push |
| Jaeger Thrift | 14268 | /api/traces | Legacy Jaeger clients |
| Zipkin | 9411 | /api/v2/spans | Legacy Zipkin clients |

## CI Integration (otel-cli)

Send traces from GitHub Actions:

```bash
# Install otel-cli
curl -LO https://github.com/equinix-labs/otel-cli/releases/download/v0.4.5/otel-cli_0.4.5_linux_amd64.tar.gz
tar xzf otel-cli_0.4.5_linux_amd64.tar.gz

# Configure endpoint (via Ingress or port-forward)
export OTEL_EXPORTER_OTLP_ENDPOINT="https://tempo.goldenpath.dev"

# Wrap build steps
./otel-cli exec --name "docker-build" -- docker build -t myapp .
./otel-cli exec --name "trivy-scan" -- trivy image myapp
```

## Related

- [ADR-0055](../../docs/adrs/ADR-0055-platform-tempo-tracing-backend.md) - Tempo as standard tracing backend
- [ADR-0054](../../docs/adrs/ADR-0054-platform-observability-exporters-otel-split.md) - OTel exporter split
