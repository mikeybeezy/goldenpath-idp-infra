---
id: 20_TOOLING_APPS_MATRIX
title: Platform Tooling Apps Configuration Matrix
type: policy
risk_profile:
  production_impact: high
  security_risk: medium
  coupling_risk: high
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
  maturity: 2
relates_to:
  - 06_IDENTITY_AND_ACCESS
  - 70_OPERATIONS_README
  - ADR-0005-app-keycloak-as-identity-provider-for-human-sso
  - ADR-0006-platform-secrets-strategy
  - ADR-0055-platform-tempo-tracing-backend
  - ADR-0171-platform-application-packaging-strategy
  - ADR-0172-cd-promotion-strategy-with-approval-gates
  - CL-0131
  - CL-0136-tooling-apps-ingress-configuration
  - session-capture-2026-01-18-local-dev-hello-app
tags:
  - tooling
  - configuration
  - operations
  - living-doc
value_quantification:
  vq_class: 🔴 HV/HQ
  impact_tier: high
  potential_savings_hours: 8.0
category: compliance
supported_until: 2028-01-15
version: 1.0
breaking_change: false
---

## Platform Tooling Apps Configuration Matrix

This living document captures the configuration requirements, dependencies, and operational status of all platform tooling applications deployed via Argo CD.

**Last Updated**: 2026-01-21
**Maintainer**: platform-team
**Signed**: platform-team (2026-01-21)

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
|**Kong Manager**|`https://kong.dev.goldenpathidp.io`|`kubectl port-forward svc/dev-kong-kong-manager -n kong-system 8002:8002`|kong-system|
|**hello-goldenpath-idp**|`https://hello-goldenpath-idp.dev.goldenpathidp.io`|`kubectl port-forward svc/hello-goldenpath-idp -n apps 8080:80`|apps|
|**Prometheus**|Internal only|`kubectl port-forward svc/kube-prometheus-stack-prometheus -n monitoring 9090:9090`|monitoring|
|**Alertmanager**|Internal only|`kubectl port-forward svc/kube-prometheus-stack-alertmanager -n monitoring 9093:9093`|monitoring|

### Staging Environment

|Service|URL|
|---------|-----|
|**Backstage**|`https://backstage.staging.goldenpathidp.io`|
|**Keycloak**|`https://keycloak.staging.goldenpathidp.io`|
|**ArgoCD**|`https://argocd.staging.goldenpathidp.io`|
|**Grafana**|`https://grafana.staging.goldenpathidp.io`|
|**Kong Manager**|`https://kong.staging.goldenpathidp.io`|
|**hello-goldenpath-idp**|`https://hello-goldenpath-idp.staging.goldenpathidp.io`|

### Production Environment

|Service|URL|
|---------|-----|
|**Backstage**|`https://backstage.goldenpathidp.io`|
|**Keycloak**|`https://keycloak.goldenpathidp.io`|
|**ArgoCD**|`https://argocd.goldenpathidp.io`|
|**Grafana**|`https://grafana.goldenpathidp.io`|
|**Kong Manager**|`https://kong.goldenpathidp.io`|
|**hello-goldenpath-idp**|`https://hello-goldenpath-idp.goldenpathidp.io`|

### DNS Requirements

All URLs require DNS records pointing to the Kong LoadBalancer:

```bash
# Get Kong LoadBalancer address
kubectl get svc -n kong-system kong-kong-proxy -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'

# Verify ingress resources
kubectl get ingress -A
```

Wildcard DNS is managed by ExternalDNS from Kong Service annotations. Do not create manual wildcard records in Route53 for env subdomains.

### Certificate Issuers

|Environment|Issuer|Notes|
|-------------|--------|-------|
|dev|`letsencrypt-staging`|Staging certs (browser warnings expected)|
|staging|`letsencrypt-staging`|Staging certs|
|prod|`letsencrypt-prod`|Production certs (trusted)|

---

## Component Categories

The platform tooling is organized into four tiers based on deployment layer and user visibility:

| Tier | Category | Description | Deploy Method |
|------|----------|-------------|---------------|
| **Tier 1** | EKS Managed Add-ons | AWS-managed components tied to cluster lifecycle | Terraform EKS |
| **Tier 2** | Platform Infrastructure | Core infrastructure required before apps deploy | Argo CD / Helm |
| **Tier 3** | Platform Services | Shared services (identity, secrets, observability) | Argo CD / Helm |
| **Tier 4** | Developer-Facing Apps | End-user accessible portals and tools | Argo CD / Helm |

---

## Tier 1: EKS Managed Add-ons

These components are managed by AWS EKS add-on system. Versions are tied to the EKS cluster version and managed via Terraform.

| Add-on | Namespace | EKS Version | Add-on Version | Status | Terraform Resource |
|--------|-----------|-------------|----------------|--------|-------------------|
| coredns | kube-system | 1.29 | EKS-managed | Active | `aws_eks_addon.coredns` |
| kube-proxy | kube-system | 1.29 | EKS-managed | Active | `aws_eks_addon.kube_proxy` |
| vpc-cni | kube-system | 1.29 | EKS-managed | Active | `aws_eks_addon.vpc_cni` |
| aws-ebs-csi-driver | kube-system | 1.29 | EKS-managed | Active | `aws_eks_addon.ebs_csi` |
| aws-efs-csi-driver | kube-system | 1.29 | EKS-managed | Active | `aws_eks_addon.efs_csi` |
| snapshot-controller | kube-system | 1.29 | EKS-managed | Active | `aws_eks_addon.snapshot_controller` |

**Version Management**: EKS add-on versions are configured in `envs/{env}/terraform.tfvars` via `addon_versions` map. When not specified, AWS selects the recommended version for the cluster.

**Terraform Reference**: `modules/aws_eks/main.tf` (lines 190-301)

---

## Tier 2: Platform Infrastructure

Core infrastructure components that must be running before platform services or applications can deploy.

| App | Namespace | Chart | Chart Version | Image Tag | Status | Sync-Wave |
|-----|-----------|-------|---------------|-----------|--------|-----------|
| [cluster-autoscaler](#cluster-autoscaler) | kube-system | kubernetes/autoscaler | 9.43.0 | v1.29.0 | Configured | -1 |
| [aws-load-balancer-controller](#aws-load-balancer-controller) | kube-system | eks/aws-load-balancer-controller | 1.7.1 | v2.7.1 | Configured | -1 |
| [metrics-server](#metrics-server) | kube-system | metrics-server/metrics-server | 3.12.0 | v0.7.0 | Bootstrap | N/A |

---

## Tier 3: Platform Services

Shared services providing capabilities to applications. Ordered by sync-wave for dependency management.

| App | Namespace | Chart | Chart Version | Image Tag | Status | Sync-Wave |
|-----|-----------|-------|---------------|-----------|--------|-----------|
| [external-secrets](#external-secrets) | external-secrets | external-secrets/external-secrets | 0.9.13 | v0.9.13 | Configured | 0 |
| cluster-secret-store | external-secrets | Kustomize | N/A | N/A | Configured | 1 |
| [external-dns](#external-dns) | kube-system | external-dns/external-dns | 1.14.5 | v0.14.0 | Configured | 0 |
| [cert-manager](#cert-manager) | cert-manager | jetstack/cert-manager | v1.14.4 | v1.14.4 | Configured | 0 |
| [argocd-image-updater](#argocd-image-updater) | argocd | argoproj/argocd-image-updater | 0.9.1 | v0.12.2 | Configured | 0 |
| [kong](#kong) | kong-system | konghq/kong | 2.47.0 | 3.6.1 | Configured | 2 |
| [keycloak](#keycloak) | keycloak | bitnami/keycloak | 25.2.0 | 26.3.3 | Configured | 3 |
| [kube-prometheus-stack](#kube-prometheus-stack) | monitoring | prometheus-community/kube-prometheus-stack | 45.7.1 | v2.47.2 | Configured | 4 |
| [loki](#loki) | monitoring | grafana/loki-stack | 2.9.11 | 2.9.4 | Configured | 4 |
| [tempo](#tempo) | monitoring | grafana/tempo | 1.10.x | 2.3.1 | Configured | 4 |
| [fluent-bit](#fluent-bit) | monitoring | fluent/fluent-bit | 0.47.0 | 3.0.3 | Configured | 4 |

---

## Tier 4: Developer-Facing Applications

End-user accessible components including developer portals and sample applications.

| App | Namespace | Chart | Chart Version | Image Tag | Status | Sync-Wave |
|-----|-----------|-------|---------------|-----------|--------|-----------|
| [backstage](#backstage) | backstage | backstage/backstage | 2.6.3 | 1.29.0 | Configured | 5 |
| hello-goldenpath-idp | apps | Custom | N/A | latest | Sample App | 6 |

---

## Local Development Stack (Ephemeral Only)

Components for local/ephemeral development environments. Not deployed to staging/prod.

| App | Namespace | Chart | Chart Version | Image Tag | Status |
|-----|-----------|-------|---------------|-----------|--------|
| [localstack](#localstack) | local-infra | localstack/localstack | 3.0.0 | 3.0.0 | Standard |
| [minio](#minio) | local-infra | minio/minio | 5.0.0 | RELEASE.2024-01 | Standard |
| [postgresql](#postgresql) | local-infra | bitnami/postgresql | 13.2.24 | 15.6.0 | Standard |

---

## Status and Priority Keys

**Status Key**:

- **Active**: EKS-managed add-on, automatically updated
- **Configured**: Values file has required configuration
- **Bootstrap**: Installed via bootstrap script, not Argo CD
- **Standard**: Standard mock stack for Ephemeral/Local environments
- **Partial**: Has some config but missing critical pieces
- **Minimal**: Basic config only (e.g., storage mode)
- **Needs Config**: Only governance metadata, no actual values

**Sync-Wave Key** (Argo CD deployment order):

- **-1**: Pre-requisites (infrastructure controllers)
- **0**: Foundation (secrets, DNS, certificates)
- **1**: Secret stores
- **2**: Ingress gateway
- **3**: Identity provider
- **4**: Observability stack
- **5**: Developer portal
- **6**: Sample applications

---

## Dependency Graph

```text
                    ┌─────────────────┐
                    │ external-secrets│  P0 - Foundation
                    │  (AWS Secrets)  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  external-dns   │  P0 - Foundation
                    │ (Route53 DNS)   │
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

     ┌───────────────────────────────────────────────────────────┐
     │                   OBSERVABILITY STACK                     │
     │  ┌───────────┐  ┌──────┐  ┌───────┐  ┌──────────────┐     │
     │  │ fluent-bit│─►│ loki │  │ tempo │◄─│ prometheus   │     │
     │  │  (logs)   │  │      │  │(traces)│  │  + grafana   │     │
     │  └───────────┘  └──┬───┘  └───┬───┘  └──────┬───────┘     │
     │                    │          │             │              │
     │                    └──────────┴─────────────┘              │
     │                           ▼                                │
     │                    ┌────────────┐                          │
     │                    │  Grafana   │                          │
     │                    │ (unified)  │                          │
     │                    └────────────┘                          │
     └───────────────────────────────────────────────────────────┘
```

---

## Application Details

### Tier 1: EKS Managed Add-ons

#### coredns

**Purpose**: Provides DNS resolution within the Kubernetes cluster

| Attribute | Value |
|-----------|-------|
| Type | EKS Managed Add-on |
| Namespace | kube-system |
| Version | EKS-managed (tied to cluster version) |
| Terraform Resource | `aws_eks_addon.coredns` |
| Terraform File | `modules/aws_eks/main.tf:254-270` |

**Configuration**: Versions managed via `addon_versions` map in `envs/{env}/terraform.tfvars`. When not specified, AWS selects the recommended version.

---

#### kube-proxy

**Purpose**: Network proxy that maintains network rules for pod communication

| Attribute | Value |
|-----------|-------|
| Type | EKS Managed Add-on |
| Namespace | kube-system |
| Version | EKS-managed (tied to cluster version) |
| Terraform Resource | `aws_eks_addon.kube_proxy` |
| Terraform File | `modules/aws_eks/main.tf:272-288` |

---

#### vpc-cni

**Purpose**: Amazon VPC CNI plugin for pod networking using VPC IP addresses

| Attribute | Value |
|-----------|-------|
| Type | EKS Managed Add-on |
| Namespace | kube-system |
| Version | EKS-managed (tied to cluster version) |
| Terraform Resource | `aws_eks_addon.vpc_cni` |
| Terraform File | `modules/aws_eks/main.tf:290-306` |

---

#### aws-ebs-csi-driver

**Purpose**: CSI driver for Amazon EBS volumes (persistent block storage)

| Attribute | Value |
|-----------|-------|
| Type | EKS Managed Add-on |
| Namespace | kube-system |
| Version | EKS-managed |
| Terraform Resource | `aws_eks_addon.ebs_csi` |
| Terraform File | `modules/aws_eks/main.tf:188-212` |
| IRSA | Required for EBS operations |

**Dependencies**:
- **Upstream**: IRSA role with EBS permissions
- **Downstream**: StorageClass `gp3`, PVCs for stateful workloads

---

#### aws-efs-csi-driver

**Purpose**: CSI driver for Amazon EFS (shared filesystem for ReadWriteMany)

| Attribute | Value |
|-----------|-------|
| Type | EKS Managed Add-on |
| Namespace | kube-system |
| Version | EKS-managed |
| Terraform Resource | `aws_eks_addon.efs_csi` |
| Terraform File | `modules/aws_eks/main.tf:214-238` |
| IRSA | Required for EFS operations |

**Dependencies**:
- **Upstream**: IRSA role with EFS permissions, EFS filesystem
- **Downstream**: StorageClass `efs-sc`, PVCs requiring shared storage

---

#### snapshot-controller

**Purpose**: Manages VolumeSnapshot CRDs for backup/restore operations

| Attribute | Value |
|-----------|-------|
| Type | EKS Managed Add-on |
| Namespace | kube-system |
| Version | EKS-managed |
| Terraform Resource | `aws_eks_addon.snapshot_controller` |
| Terraform File | `modules/aws_eks/main.tf:239-252` |

---

### Tier 2: Platform Infrastructure

#### cluster-autoscaler

**Purpose**: Automatically adjusts node group size based on pod scheduling needs

| Attribute | Value |
|-----------|-------|
| Chart | kubernetes/autoscaler |
| Chart Version | 9.43.0 |
| Image Tag | v1.29.0 |
| Namespace | kube-system |
| Argo App | `gitops/argocd/apps/dev/cluster-autoscaler.yaml` |
| Values File | `gitops/helm/cluster-autoscaler/values/dev.yaml` |
| Risk Level | Medium |

#### cluster-autoscaler Required Configuration

| Config Item | Description | Source | Status |
|-------------|-------------|--------|--------|
| ServiceAccount IRSA | IAM role for ASG operations | Terraform output | Configured |
| cloudProvider | Set to `aws` | Values file | Configured |
| autoDiscovery.clusterName | EKS cluster name | Values file | Configured |

#### cluster-autoscaler Dependencies

- **Upstream**: IRSA role with autoscaling permissions, EKS node groups with proper tags
- **Downstream**: All workloads requiring dynamic scaling

---

#### aws-load-balancer-controller

**Purpose**: Manages AWS ALB/NLB resources for Kubernetes Ingress and Service objects

| Attribute | Value |
|-----------|-------|
| Chart | eks/aws-load-balancer-controller |
| Chart Version | 1.7.1 |
| Image Tag | v2.7.1 |
| Namespace | kube-system |
| Deploy Method | Bootstrap script |
| Bootstrap File | `bootstrap/30_core-addons/10_aws_lb_controller.sh` |
| Risk Level | High |

#### aws-load-balancer-controller Required Configuration

| Config Item | Description | Source | Status |
|-------------|-------------|--------|--------|
| ServiceAccount IRSA | IAM role for ALB/NLB operations | Terraform output | Configured |
| clusterName | EKS cluster name | Values/CLI | Configured |
| vpcId | VPC ID for load balancer placement | Terraform output | Configured |

#### aws-load-balancer-controller Dependencies

- **Upstream**: IRSA role (`goldenpath-idp-aws-load-balancer-controller`), VPC subnets with proper tags
- **Downstream**: Kong (LoadBalancer Service), Ingress resources

---

#### metrics-server

**Purpose**: Provides resource metrics (CPU/memory) for HPA and `kubectl top`

| Attribute | Value |
|-----------|-------|
| Chart | metrics-server/metrics-server |
| Chart Version | 3.12.0 |
| Image Tag | v0.7.0 |
| Namespace | kube-system |
| Deploy Method | Bootstrap script |
| Bootstrap File | `bootstrap/10_bootstrap/goldenpath-idp-bootstrap.sh` |
| Risk Level | Low |

#### metrics-server Dependencies

- **Upstream**: None (standalone)
- **Downstream**: HPA, `kubectl top nodes/pods`, Cluster Autoscaler decisions

---

### Tier 3: Platform Services

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

---

### external-dns

**Purpose**: Manages Route53 records from Kubernetes Services and Ingresses

|Attribute|Value|
|---------|-----|
|Chart|external-dns/external-dns|
|Chart Version|1.14.5|
|Image Tag|v0.14.0|
|Namespace|kube-system|
|Argo App|`gitops/argocd/apps/dev/external-dns.yaml`|
|Values File|`gitops/helm/external-dns/values/dev.yaml`|
|Risk Level|Low (DNS-critical dependency)|

#### external-dns Required Configuration

|Config Item|Description|Source|Status|
|-----------|-----------|------|------|
|ServiceAccount IRSA|IAM role scoped to Route53 hosted zone|Terraform output|Configured|
|Domain Filters|Limit records to env subdomain|Values file|Configured|
|TXT Registry|Ownership/lock for records|Values file|Configured|
|Wildcard Annotation|Kong Service annotation `*.{env}.goldenpathidp.io`|Kong values|Configured|

#### external-dns Dependencies

- **Upstream**: EKS OIDC provider (IRSA)
- **Downstream**: Kong proxy Service, Ingress resources for tooling apps

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
    - name: Tempo
      type: tempo
      access: proxy
      url: http://tempo.monitoring.svc:3100
      jsonData:
        tracesToLogsV2:
          datasourceUid: loki
          tags: ['job', 'namespace', 'pod']
        serviceMap:
          datasourceUid: prometheus
        nodeGraph:
          enabled: true
        lokiSearch:
          datasourceUid: loki
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

### tempo

**Purpose**: Distributed tracing backend for OpenTelemetry traces

|Attribute|Value|
|---------|-----|
|Chart|grafana/tempo|
|Chart Version|1.10.x|
|Image Tag|2.3.1|
|Namespace|monitoring|
|Argo App|`gitops/argocd/apps/dev/tempo.yaml`|
|Values File|`gitops/helm/tempo/values/dev.yaml`|
|Risk Level|Low|
|ADR|ADR-0055|

#### tempo Required Configuration

|Config Item|Description|Source|Status|
|-----------|-----------|------|------|
|deploymentMode|SingleBinary (dev) or Distributed (prod)|Values file|Configured|
|storage.trace.backend|local (dev) or s3 (staging/prod)|Values file|Configured|
|retention|Trace retention period|Values file|Configured|
|receivers.otlp|OTLP gRPC and HTTP endpoints|Values file|Configured|

#### Tempo Configuration by Environment

|Environment|Mode|Storage|Retention|
|-----------|------|-------|---------|
|dev|SingleBinary|local|3 days|
|test|SingleBinary|local|7 days|
|staging|SingleBinary|S3|14 days|
|prod|Distributed|S3|30 days|

#### Ingestion Endpoints

|Protocol|Port|Use Case|
|--------|------|--------|
|OTLP gRPC|4317|High-volume apps, otel-cli|
|OTLP HTTP|4318|Simple HTTP push|
|Jaeger|14268|Legacy Jaeger clients|
|Zipkin|9411|Legacy Zipkin clients|

#### Minimum Values Required (Dev)

```yaml
tempo:
  image:
    repository: grafana/tempo
    tag: 2.3.1

  retention: 72h

  storage:
    trace:
      backend: local
      local:
        path: /var/tempo/traces

  receivers:
    otlp:
      protocols:
        grpc:
          endpoint: 0.0.0.0:4317
        http:
          endpoint: 0.0.0.0:4318

persistence:
  enabled: true
  size: 5Gi

serviceMonitor:
  enabled: true
  namespace: monitoring
  labels:
    release: kube-prometheus-stack
```

#### tempo Dependencies

- **Upstream**: Storage (local or S3), ServiceAccount (IRSA for S3)
- **Downstream**: Grafana (visualization), otel-cli (CI traces), App OTel SDKs

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

### argocd-image-updater

**Purpose**: Automated image tag updates from container registries to GitOps repositories

|Attribute|Value|
|---------|-----|
|Chart|argoproj/argocd-image-updater|
|Chart Version|0.9.1|
|Image Tag|v0.12.2|
|Namespace|argocd|
|Argo App|`gitops/argocd/apps/dev/argocd-image-updater.yaml`|
|Values File|`gitops/helm/argocd-image-updater/values/dev.yaml`|
|Risk Level|Medium|
|ADR|ADR-0172|

#### argocd-image-updater Required Configuration

|Config Item|Description|Source|Status|
|-----------|-----------|------|------|
|config.argocd.serverAddress|Argo CD server address|Values file|Configured|
|config.registries|ECR registry configuration|Values file|Configured|
|config.gitCommitUser|Git commit author|Values file|Configured|
|serviceAccount|IRSA for ECR access|Values file|Configured|

#### Image Update Strategies

|Strategy|Description|Use Case|
|--------|-----------|--------|
|`latest`|Always use most recent tag|dev/test|
|`semver`|Follow semantic versioning|staging/prod|
|`digest`|Pin exact image digest|security-critical|

#### Application Annotations Required

```yaml
# For apps managed by Image Updater
metadata:
  annotations:
    argocd-image-updater.argoproj.io/image-list: app=<ecr-repo>
    argocd-image-updater.argoproj.io/app.update-strategy: latest|semver
    argocd-image-updater.argoproj.io/write-back-method: git
    argocd-image-updater.argoproj.io/git-branch: main
```

#### Sync Policy by Environment (ADR-0172)

|Environment|App Sync|Image Strategy|Rationale|
|-----------|--------|--------------|---------|
|dev|automated|latest|Fast iteration|
|test|automated|latest|Integration testing|
|staging|automated|semver|Pre-prod validation|
|prod|**manual**|semver|Explicit approval required|

#### argocd-image-updater Dependencies

- **Upstream**: Argo CD, ECR (registry access), Git (write-back)
- **Downstream**: All application deployments using image automation

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
|2026-01-18|platform-team|Added Tempo distributed tracing backend (ADR-0055)|
|2026-01-18|platform-team|Added Tempo datasource to kube-prometheus-stack Grafana config|
|2026-01-18|platform-team|Updated observability stack dependency graph to include Tempo|
|2026-01-18|platform-team|Added Argo CD Image Updater for automated image tag updates (ADR-0172)|
|2026-01-21|platform-team|Added Kong Manager UI and hello-goldenpath-idp to tooling access URLs|
|2026-01-21|platform-team|Restructured matrix into 4-tier component categories (EKS Add-ons, Infrastructure, Services, Apps)|
|2026-01-21|platform-team|Added EKS managed add-ons: coredns, kube-proxy, vpc-cni, ebs-csi, efs-csi, snapshot-controller|
|2026-01-21|platform-team|Added infrastructure components: cluster-autoscaler, aws-load-balancer-controller, metrics-server|
|2026-01-21|platform-team|Added sync-wave ordering to quick reference tables|

---

## References

- [ADR-0005: Keycloak as Identity Provider](../adrs/ADR-0005-app-keycloak-as-identity-provider-for-human-sso.md)
- [ADR-0006: Vault for Secret Management](../adrs/ADR-0006-app-hashicorp-vault-for-secret-management.md)
- [ADR-0055: Tempo Tracing Backend](../adrs/ADR-0055-platform-tempo-tracing-backend.md)
- [ADR-0171: Application Packaging Strategy](../adrs/ADR-0171-platform-application-packaging-strategy.md)
- [ADR-0172: CD Promotion Strategy](../adrs/ADR-0172-cd-promotion-strategy-with-approval-gates.md)
- [Bootstrap Scripts](../../bootstrap/10_bootstrap/)
- [Argo CD Apps](../../gitops/argocd/apps/)
