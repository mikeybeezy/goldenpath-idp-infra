---
id: 20_TOOLING_APPS_MATRIX
title: Platform Tooling Apps Configuration Matrix
type: reference
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: high
  security_risk: medium
  coupling_risk: high
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
  maturity: 2
schema_version: 1
relates_to:
  - 06_IDENTITY_AND_ACCESS
  - 70_OPERATIONS_README
  - ADR-0005-app-keycloak-as-identity-provider-for-human-sso
  - ADR-0006-platform-secrets-strategy
  - CL-0131
  - CL-0136-tooling-apps-ingress-configuration
supersedes: []
superseded_by: []
tags:
  - tooling
  - configuration
  - operations
  - living-doc
inheritance: {}
value_quantification:
  vq_class: HV/HQ
  impact_tier: high
  potential_savings_hours: 8.0
supported_until: 2028-01-15
version: 1.0
breaking_change: false
---
## Platform Tooling Apps Configuration Matrix

This living document captures the configuration requirements, dependencies, and operational status of all platform tooling applications deployed via Argo CD.

**Last Updated**: 2026-01-16
**Maintainer**: platform-team

---

## Tooling Access URLs

All platform tooling applications are accessible via Kong Ingress with TLS termination via cert-manager.

### Dev Environment

|Service|URL|Port-Forward Fallback|Namespace|
|---------|-----|----------------------|-----------|
|**Backstage**|`https://backstage.dev.goldenpathidp.io`|`kubectl port-forward svc/dev-backstage -n backstage 7007:7007`|backstage|
|**Keycloak**|`https://keycloak.dev.goldenpathidp.io`|`kubectl port-forward svc/dev-keycloak -n keycloak 8080:8080`|keycloak|
|**ArgoCD**|`https://argocd.dev.goldenpathidp.io`|`kubectl port-forward svc/argocd-server -n argocd 8080:443`|argocd|
|**Grafana**|`https://grafana.dev.goldenpathidp.io`|`kubectl port-forward svc/kube-prometheus-stack-grafana -n monitoring 3000:80`|monitoring|
|**Prometheus**|Internal only|`kubectl port-forward svc/kube-prometheus-stack-prometheus -n monitoring 9090:9090`|monitoring|
|**Alertmanager**|Internal only|`kubectl port-forward svc/kube-prometheus-stack-alertmanager -n monitoring 9093:9093`|monitoring|

### Staging Environment

|Service|URL|
|---------|-----|
|**Backstage**|`https://backstage.staging.goldenpathidp.io`|
|**Keycloak**|`https://keycloak.staging.goldenpathidp.io`|
|**ArgoCD**|`https://argocd.staging.goldenpathidp.io`|
|**Grafana**|`https://grafana.staging.goldenpathidp.io`|

### Production Environment

|Service|URL|
|---------|-----|
|**Backstage**|`https://backstage.goldenpathidp.io`|
|**Keycloak**|`https://keycloak.goldenpathidp.io`|
|**ArgoCD**|`https://argocd.goldenpathidp.io`|
|**Grafana**|`https://grafana.goldenpathidp.io`|

### DNS Requirements

All URLs require DNS records pointing to the Kong LoadBalancer:

```bash
# Get Kong LoadBalancer address
kubectl get svc -n kong-system kong-kong-proxy -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'

# Verify ingress resources
kubectl get ingress -A
```

For wildcard DNS, configure `*.dev.goldenpathidp.io`, `*.staging.goldenpathidp.io`, and `*.goldenpathidp.io` to point to the respective Kong LoadBalancer addresses.

### Certificate Issuers

|Environment|Issuer|Notes|
|-------------|--------|-------|
|dev|`letsencrypt-staging`|Staging certs (browser warnings expected)|
|staging|`letsencrypt-staging`|Staging certs|
|prod|`letsencrypt-prod`|Production certs (trusted)|

---

## Quick Reference

|App|Namespace|Chart|Chart Version|Image Tag|Status|Priority|
|---|---------|-----|-------------|---------|------|--------|
|[external-secrets](#external-secrets)|external-secrets|external-secrets/external-secrets|0.9.13|v0.9.13|Configured|P0|
|[cert-manager](#cert-manager)|cert-manager|jetstack/cert-manager|v1.14.4|v1.14.4|Configured|P0|
|[keycloak](#keycloak)|keycloak|bitnami/keycloak|25.2.0|26.3.3|Configured|P1|
|[kong](#kong)|kong-system|konghq/kong|2.47.0|3.6.1|Configured|P1|
|[backstage](#backstage)|backstage|backstage/backstage|2.6.3|1.29.0|Configured|P2|
|[kube-prometheus-stack](#kube-prometheus-stack)|monitoring|prometheus-community/kube-prometheus-stack|45.7.1|v2.47.2|Configured|P3|
|[loki](#loki)|monitoring|grafana/loki-stack|2.9.11|2.9.4|Configured|P3|
|[fluent-bit](#fluent-bit)|monitoring|fluent/fluent-bit|0.47.0|3.0.3|Configured|P3|
|[localstack](#localstack)|local-infra|localstack/localstack|3.0.0|3.0.0|Standard (Ephem)|P0|
|[minio](#minio)|local-infra|minio/minio|5.0.0|RELEASE.2024-01|Standard (Ephem)|P0|
|[postgresql](#postgresql)|local-infra|bitnami/postgresql|13.2.24|15.6.0|Standard (Ephem)|P0|

**Status Key**:

- **Configured**: Values file has required configuration
- **Standard (Ephem)**: Standard mock stack for Ephemeral/Local environments
- **Partial**: Has some config but missing critical pieces
- **Minimal**: Basic config only (e.g., storage mode)
- **Needs Config**: Only governance metadata, no actual values

**Priority Key**:

- **P0**: Foundation - must be configured first (other apps depend on it)
- **P1**: Core Platform - identity and API gateway
- **P2**: Developer Experience - portals and tooling
- **P3**: Observability - monitoring and logging

---

## Dependency Graph

```text
                    ┌─────────────────┐
                    │ external-secrets│  P0 - Foundation
                    │  (AWS Secrets)  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  cert-manager   │  P0 - Foundation
                    │ (TLS Certs)     │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼────────┐     │     ┌────────▼────────┐
     │    keycloak     │     │     │      kong       │
     │  (Identity/SSO) │◄────┼────►│  (API Gateway)  │
     └────────┬────────┘     │     └────────┬────────┘
              │              │              │
              │    ┌─────────▼─────────┐    │
              └───►│    backstage      │◄───┘
                   │ (Developer Portal)│
                   └───────────────────┘

     ┌─────────────────────────────────────────────┐
     │              OBSERVABILITY STACK            │
     │  ┌───────────┐  ┌──────┐  ┌──────────────┐  │
     │  │ fluent-bit│─►│ loki │◄─│ prometheus   │  │
     │  │  (logs)   │  │      │  │  + grafana   │  │
     │  └───────────┘  └──────┘  └──────────────┘  │
     └─────────────────────────────────────────────┘
```

---

## Application Details

### external-secrets

**Purpose**: Syncs secrets from AWS Secrets Manager into Kubernetes Secrets

|Attribute|Value|
|---------|-----|
|Chart|external-secrets/external-secrets|
|Chart Version|0.9.13|
|Image Tag|v0.9.13|
|Namespace|external-secrets|
|Argo App|`gitops/argocd/apps/dev/external-secrets.yaml`|
|Values File|`gitops/helm/external-secrets/values/dev.yaml`|
|Risk Level|Low (but critical dependency)|

#### external-secrets Required Configuration

|Config Item|Description|Source|Status|
|-----------|-----------|------|------|
|ServiceAccount IRSA|IAM role for AWS Secrets Manager access|Terraform output|Configured|
|ClusterSecretStore|Points to AWS Secrets Manager backend|Kustomize|Configured|
|RefreshInterval|How often to sync secrets|Values file|Default (1h)|

#### ClusterSecretStore Required

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata:
  name: aws-secretsmanager
spec:
  provider:
    aws:
      service: SecretsManager
      region: eu-west-2
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets
            namespace: external-secrets
```

#### external-secrets Dependencies

- **Upstream**: AWS IAM Role (IRSA), AWS Secrets Manager
- **Downstream**: All apps requiring secrets (Keycloak, Backstage, Kong)

#### Secrets This App Provides

|Secret Name|Consumers|AWS SM Path|
|-------------|-----------|-------------|
|keycloak-admin|Keycloak|`goldenpath/dev/keycloak/admin`|
|backstage-github-token|Backstage|`goldenpath/dev/backstage/secrets`|
|backstage-db-credentials|Backstage|`goldenpath/dev/backstage/postgres`|
|kong-admin-credentials|Kong|`goldenpath/dev/kong/admin`|

---

### cert-manager

**Purpose**: Automated TLS certificate management via Let's Encrypt or internal CA

|Attribute|Value|
|---------|-----|
|Chart|jetstack/cert-manager|
|Chart Version|v1.14.4|
|Image Tag|v1.14.4|
|Namespace|cert-manager|
|Argo App|`gitops/argocd/apps/dev/cert-manager.yaml`|
|Values File|`gitops/helm/cert-manager/values/dev.yaml`|
|Risk Level|Medium|

#### cert-manager Required Configuration

|Config Item|Description|Source|Status|
|-----------|-----------|------|------|
|installCRDs|Install Certificate CRDs|Values file|Configured|
|ClusterIssuer|Let's Encrypt or self-signed issuer|Kustomize|Configured|
|DNS01 Solver|Route53 credentials for DNS challenge|External Secrets|N/A (HTTP01)|

#### ClusterIssuer Required (Let's Encrypt)

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: platform@example.com
    privateKeySecretRef:
      name: letsencrypt-prod-key
    solvers:
      - http01:
          ingress:
            class: kong
```

#### ClusterIssuer Required (Self-Signed for Dev)

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: selfsigned-issuer
spec:
  selfSigned: {}
```

#### cert-manager Dependencies

- **Upstream**: DNS provider (Route53) for ACME DNS challenge
- **Downstream**: Kong (ingress TLS), Keycloak (HTTPS), Backstage (HTTPS)

---

### keycloak

**Purpose**: Identity provider for SSO across platform applications

|Attribute|Value|
|---------|-----|
|Chart|bitnami/keycloak|
|Chart Version|25.2.0|
|Image Tag|26.3.3|
|Namespace|keycloak|
|Argo App|`gitops/argocd/apps/dev/keycloak.yaml`|
|Values File|`gitops/helm/keycloak/values/dev.yaml`|
|Risk Level|High|
|ADR|ADR-0005|

#### keycloak Required Configuration

|Config Item|Description|Source|Status|
|-----------|-----------|------|------|
|auth.adminUser|Admin username|Values file|Configured|
|auth.adminPassword|Admin password|External Secret|Configured|
|postgresql.enabled|Enable bundled PostgreSQL|Values file|Configured|
|postgresql.auth.password|PostgreSQL password|External Secret|Configured|
|proxy|Proxy mode (edge/passthrough)|Values file|Configured|
|production|Production mode flag|Values file|Configured|
|replicaCount|Number of replicas|Values file|Configured|

#### Minimum Values Required

```yaml
auth:
  adminUser: admin
  existingSecret: keycloak-admin-secret
  passwordSecretKey: admin-password

postgresql:
  enabled: true
  auth:
    existingSecret: keycloak-postgres-secret
    secretKeys:
      adminPasswordKey: postgres-password

proxy: edge
production: false  # true for prod
replicaCount: 1    # 2+ for prod

service:
  type: ClusterIP

ingress:
  enabled: true
  ingressClassName: kong
  hostname: keycloak.dev.goldenpathidp.io
  tls: true
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
```

#### OIDC Clients Required

|Client ID|Purpose|Redirect URIs|
|-----------|---------|---------------|
|backstage|Backstage SSO|`https://backstage.dev.goldenpathidp.io/api/auth/oidc/handler/frame`|
|kong|Kong Admin SSO|`https://kong.dev.goldenpathidp.io/callback`|
|argocd|Argo CD SSO|`https://argocd.dev.goldenpathidp.io/auth/callback`|
|grafana|Grafana SSO|`https://grafana.dev.goldenpathidp.io/login/generic_oauth`|

#### keycloak Dependencies

- **Upstream**: external-secrets, cert-manager, PostgreSQL (bundled or external)
- **Downstream**: Kong (OIDC), Backstage (SSO), Argo CD (SSO), Grafana (SSO)

---

### kong

**Purpose**: API Gateway and Ingress Controller

|Attribute|Value|
|---------|-----|
|Chart|konghq/kong|
|Chart Version|2.47.0|
|Image Tag|3.6.1|
|Ingress Controller Tag|3.1.2|
|Namespace|kong-system|
|Argo App|`gitops/argocd/apps/dev/kong.yaml`|
|Values File|`gitops/helm/kong/values/dev.yaml`|
|Risk Level|High|

#### kong Required Configuration

|Config Item|Description|Source|Status|
|-----------|-----------|------|------|
|proxy.type|LoadBalancer for external access|Values file|Configured|
|admin.enabled|Enable Admin API|Values file|Configured|
|env.database|Database backend (off/postgres)|Values file|Configured (off)|
|ingressController.enabled|Enable K8s ingress controller|Values file|Configured|

#### kong Additional Values Required

```yaml
admin:
  enabled: true
  type: ClusterIP
  http:
    enabled: true

manager:
  enabled: true
  type: ClusterIP
  ingress:
    enabled: true
    ingressClassName: kong
    hostname: kong-admin.dev.goldenpathidp.io

env:
  database: "off"  # DB-less mode for dev
  # Or for DB mode:
  # database: postgres
  # pg_host: kong-postgresql
  # pg_password:
  #   valueFrom:
  #     secretKeyRef:
  #       name: kong-postgres-secret
  #       key: password

ingressController:
  enabled: true
  installCRDs: false  # Already installed
```

#### Plugins to Configure

|Plugin|Purpose|Config Location|
|--------|---------|-----------------|
|rate-limiting|API rate limits|KongPlugin CRD|
|oidc|Keycloak authentication|KongPlugin CRD|
|cors|Cross-origin requests|KongPlugin CRD|
|request-transformer|Header manipulation|KongPlugin CRD|

#### kong Dependencies

- **Upstream**: cert-manager (TLS), external-secrets (credentials)
- **Downstream**: All ingress traffic, Backstage, Keycloak admin

---

### backstage

**Purpose**: Internal Developer Portal and Service Catalog

|Attribute|Value|
|---------|-----|
|Chart|backstage/backstage|
|Chart Version|2.6.3|
|Image Tag|1.29.0|
|PostgreSQL Tag|15.6.0-debian-12-r8|
|Namespace|backstage|
|Argo App|`gitops/argocd/apps/dev/backstage.yaml`|
|Values File|`gitops/helm/backstage/values/dev.yaml`|
|Risk Level|Medium|

#### backstage Required Configuration

|Config Item|Description|Source|Status|
|-----------|-----------|------|------|
|appConfig.app.baseUrl|Frontend URL|Values file|Configured|
|appConfig.backend.baseUrl|Backend API URL|Values file|Configured|
|appConfig.backend.database|PostgreSQL connection|Values file|Configured|
|appConfig.auth.providers|OIDC/GitHub auth config|Values file|Configured|
|appConfig.integrations.github|GitHub API token|External Secret|Configured|

#### backstage Additional Values Required

```yaml
appConfig:
  app:
    baseUrl: https://backstage.dev.goldenpathidp.io
    title: Goldenpath IDP

  backend:
    baseUrl: https://backstage.dev.goldenpathidp.io
    database:
      client: pg
      connection:
        host: ${POSTGRES_HOST}
        port: ${POSTGRES_PORT}
        user: ${POSTGRES_USER}
        password: ${POSTGRES_PASSWORD}

  auth:
    environment: development
    providers:
      oidc:
        development:
          metadataUrl: https://keycloak.dev.goldenpathidp.io/realms/goldenpath/.well-known/openid-configuration
          clientId: backstage
          clientSecret: ${OIDC_CLIENT_SECRET}

  integrations:
    github:
      - host: github.com
        token: ${GITHUB_TOKEN}

postgresql:
  enabled: true
  auth:
    existingSecret: backstage-postgres-secret

ingress:
  enabled: true
  className: kong
  host: backstage.dev.goldenpathidp.io
```

#### backstage Dependencies

- **Upstream**: Keycloak (OIDC), external-secrets, cert-manager, PostgreSQL
- **Downstream**: Developer self-service workflows

---

### kube-prometheus-stack

**Purpose**: Metrics collection, alerting, and visualization

|Attribute|Value|
|---------|-----|
|Chart|prometheus-community/kube-prometheus-stack|
|Chart Version|45.7.1|
|Prometheus Tag|v2.47.2|
|Alertmanager Tag|v0.26.0|
|Grafana Tag|10.2.3|
|Operator Tag|v0.68.0|
|Node Exporter Tag|v1.6.1|
|Kube State Metrics Tag|v2.10.1|
|Namespace|monitoring|
|Argo App|`gitops/argocd/apps/dev/kube-prometheus-stack.yaml`|
|Values File|`gitops/helm/kube-prometheus-stack/values/dev.yaml`|
|Risk Level|Low|

#### Current Configuration

```yaml
prometheus:
  prometheusSpec:
    retention: 7d
    storageSpec:
      volumeClaimTemplate:
        spec:
          accessModes: [ReadWriteOnce]
          resources:
            requests:
              storage: 20Gi

alertmanager:
  alertmanagerSpec:
    storage:
      volumeClaimTemplate:
        spec:
          accessModes: [ReadWriteOnce]
          resources:
            requests:
              storage: 5Gi

grafana:
  persistence:
    enabled: true
    size: 10Gi
  additionalDataSources:
    - name: Loki
      type: loki
      access: proxy
      url: http://loki-gateway.monitoring.svc:3100
```

#### Optional Enhancements

|Config Item|Description|Status|
|-------------|-------------|--------|
|grafana.adminPassword|Grafana admin password|Default (prom-operator)|
|grafana.ingress|External access to Grafana|Not configured|
|alertmanager.config|Alert routing rules|Not configured|
|additionalPrometheusRules|Custom alert rules|Not configured|

#### kube-prometheus-stack Dependencies

- **Upstream**: Storage class (EBS), Loki
- **Downstream**: Platform observability

---

### loki

**Purpose**: Log aggregation and storage

|Attribute|Value|
|---------|-----|
|Chart|grafana/loki-stack|
|Chart Version|2.9.11|
|Image Tag|2.9.4|
|Gateway Tag|1.25-alpine|
|Namespace|monitoring|
|Argo App|`gitops/argocd/apps/dev/loki.yaml`|
|Values File|`gitops/helm/loki/values/dev.yaml`|
|Risk Level|Low|

#### Loki Configuration

|Config Item|Description|Status|
|-----------|-----------|------|
|deploymentMode|SingleBinary for dev|Configured|
|storage|Local filesystem for dev|Configured|
|limits_config.retention|7 days retention|Configured|

#### loki Dependencies

- **Upstream**: Storage (local or S3)
- **Downstream**: Grafana (visualization), Fluent-bit (log source)

---

### fluent-bit

**Purpose**: Log collection and forwarding to Loki

|Attribute|Value|
|---------|-----|
|Chart|fluent/fluent-bit|
|Chart Version|0.47.0|
|Image Tag|3.0.3|
|Namespace|monitoring|
|Argo App|`gitops/argocd/apps/dev/fluent-bit.yaml`|
|Values File|`gitops/helm/fluent-bit/values/dev.yaml`|
|Risk Level|Low|

#### fluent-bit Required Configuration

|Config Item|Description|Source|Status|
|-----------|-----------|------|------|
|config.outputs|Loki output destination|Values file|Configured|
|config.filters|Log parsing and enrichment|Values file|Configured|

#### Values Required

```yaml
config:
  outputs: |
    [OUTPUT]
        Name        loki
        Match       *
        Host        loki-gateway.monitoring.svc
        Port        3100
        Labels      job=fluent-bit
        auto_kubernetes_labels on

  filters: |
    [FILTER]
        Name         kubernetes
        Match        kube.*
        Merge_Log    On
        Keep_Log     Off
        K8S-Logging.Parser On
        K8S-Logging.Exclude On
```

#### fluent-bit Dependencies

- **Upstream**: Node filesystem access, Kubernetes API
- **Downstream**: Loki

---

## AWS Secrets Manager Structure

All secrets should be stored in AWS Secrets Manager with the following path convention:

```text
goldenpath/{env}/{app}/{secret-name}
```

### localstack

**Purpose**: Local AWS emulator for ephemeral/local development.

|Attribute|Value|
|---|---|
|Chart|localstack/localstack|
|Chart Version|3.0.0|
|Image Tag|3.0.0|
|Namespace|local-infra|
|Argo App|`gitops/argocd/apps/local/local-infra.yaml`|
|Values File|`gitops/helm/local-infra/values.yaml`|
|Risk Level|Low (local-only)|

#### localstack Required Configuration

- Managed via `gitops/helm/local-infra/values.yaml` when local-infra is enabled.

#### localstack Dependencies

- **Upstream**: None (local-only)
- **Downstream**: Optional (local dev/test tooling)

### minio

**Purpose**: S3-compatible object storage for ephemeral/local development.

|Attribute|Value|
|---|---|
|Chart|minio/minio|
|Chart Version|5.0.0|
|Image Tag|RELEASE.2024-01|
|Namespace|local-infra|
|Argo App|`gitops/argocd/apps/local/local-infra.yaml`|
|Values File|`gitops/helm/local-infra/values.yaml`|
|Risk Level|Low (local-only)|

#### minio Required Configuration

- Managed via `gitops/helm/local-infra/values.yaml` when local-infra is enabled.

#### minio Dependencies

- **Upstream**: None (local-only)
- **Downstream**: Optional (local dev/test tooling)

### postgresql

**Purpose**: Local PostgreSQL database for ephemeral/local development.

|Attribute|Value|
|---|---|
|Chart|bitnami/postgresql|
|Chart Version|13.2.24|
|Image Tag|15.6.0|
|Namespace|local-infra|
|Argo App|`gitops/argocd/apps/local/local-infra.yaml`|
|Values File|`gitops/helm/local-infra/values.yaml`|
|Risk Level|Low (local-only)|

#### postgresql Required Configuration

- Managed via `gitops/helm/local-infra/values.yaml` when local-infra is enabled.

#### postgresql Dependencies

- **Upstream**: None (local-only)
- **Downstream**: Optional (local dev/test tooling)

### Required Secrets

|Path|Keys|Used By|
|------|------|---------|
|`goldenpath/dev/keycloak/admin`|`admin-password`|Keycloak|
|`goldenpath/dev/keycloak/postgres`|`postgres-password`|Keycloak|
|`goldenpath/dev/backstage/postgres`|`password`, `username`, `host`|Backstage|
|`goldenpath/dev/backstage/secrets`|`token`|Backstage|
|`goldenpath/dev/backstage/oidc`|`client-secret`|Backstage|
|`goldenpath/dev/kong/admin`|`password`|Kong Manager|
|`goldenpath/dev/grafana/admin`|`password`|Grafana|

---

## Changelog

|Date|Author|Change|
|----|------|------|
|2026-01-15|platform-team|Initial matrix creation|
|2026-01-15|platform-team|Added chart/image version pinning, configured all apps|
|2026-01-15|platform-team|Bumped Keycloak (25.2.0) and Backstage (2.6.3) chart versions|
|2026-01-16|platform-team|Added Tooling Access URLs section with Kong Ingress configuration|
|2026-01-16|platform-team|Configured ingress for Backstage, ArgoCD, and Grafana across all environments|

---

## References

- [ADR-0005: Keycloak as Identity Provider](../adrs/ADR-0005-app-keycloak-as-identity-provider-for-human-sso.md)
- [ADR-0006: Vault for Secret Management](../adrs/ADR-0006-app-hashicorp-vault-for-secret-management.md)
- [Bootstrap Scripts](../../bootstrap/10_bootstrap/)
- [Argo CD Apps](../../gitops/argocd/apps/)
