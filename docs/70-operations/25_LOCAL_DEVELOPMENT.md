<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: 25_LOCAL_DEVELOPMENT
title: Local Development Environment
type: policy
value_quantification:
  vq_class: 🔴 HV/HQ
  impact_tier: tier-1
  potential_savings_hours: 2.0
category: compliance
---

## Local Development Environment

This document describes how to run the Goldenpath IDP platform locally using Kind (Kubernetes in Docker) without AWS dependencies.

## Overview

The local environment overlay provides:

- **Bundled PostgreSQL** instead of RDS
- **Static secrets** instead of ExternalSecrets/AWS Secrets Manager
- **NodePort services** instead of AWS Load Balancers
- **Nginx ingress** instead of Kong (optional)
- **Reduced resource requests** for laptop-friendly operation

This allows full platform testing without AWS costs or connectivity.

## Architecture Comparison

|Component|AWS (dev/staging/prod)|Local (Kind)|
|-----------|------------------------|--------------|
|Database|RDS PostgreSQL|Bundled PostgreSQL containers|
|Secrets|AWS Secrets Manager + ESO|Static Kubernetes Secrets|
|Ingress|Kong + AWS NLB|Nginx + NodePort|
|TLS|cert-manager + Let's Encrypt|Disabled (HTTP only)|
|Storage|EBS/EFS CSI drivers|local-path-provisioner|

## Kind Cluster Configuration

The Kind cluster config is located at `basic-kind-cluster/config.yaml`:

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: ha-cluster
nodes:
  - role: control-plane
    extraMounts:
      - hostPath: /tmp/local-path-provisioner
        containerPath: /tmp/local-path-provisioner
    extraPortMappings:
      - containerPort: 80
        hostPort: 8085
        protocol: TCP
      - containerPort: 32000
        hostPort: 7007        # Backstage
        protocol: TCP
      - containerPort: 30443
        hostPort: 30443       # Kong HTTPS
        protocol: TCP
      - containerPort: 30080
        hostPort: 8090        # Kong HTTP
      - containerPort: 3000
        hostPort: 9000        # Grafana
      - containerPort: 5001
        hostPort: 9050
      - containerPort: 3010
        hostPort: 8050
      - containerPort: 3015
        hostPort: 8040
      - containerPort: 38080
        hostPort: 38080
      - containerPort: 38200
        hostPort: 7008
    kubeadmConfigPatches:
      - |
        kind: JoinConfiguration
        nodeRegistration:
          kubeletExtraArgs:
            register-with-taints: "my-taint=presence:NoSchedule"
            node-labels: "ingress-ready=true"
  - role: worker
    extraMounts:
      - hostPath: /tmp/local-path-provisioner
        containerPath: /tmp/local-path-provisioner
```

## Quick Start

### 1. Create Kind Cluster

```bash
kind create cluster --config basic-kind-cluster/config.yaml
```

### 2. Apply Local Secrets

```bash
kubectl apply -k gitops/kustomize/overlays/local
```

This creates:

- Namespaces: `keycloak`, `backstage`, `kong`, `monitoring`, `argocd`
- Static secrets with development credentials

### 3. Install Nginx Ingress (optional)

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
```

### 4. Deploy Platform Apps

```bash
# Keycloak
helm install keycloak bitnami/keycloak \
  -n keycloak \
  -f gitops/helm/keycloak/values/local.yaml

# Backstage
helm install backstage backstage/backstage \
  -n backstage \
  -f gitops/helm/backstage/values/local.yaml

# Monitoring (optional)
helm install prometheus prometheus-community/kube-prometheus-stack \
  -n monitoring \
  -f gitops/helm/kube-prometheus-stack/values/local.yaml
```

## Local Values Files

Each tooling app has a `local.yaml` values file:

|App|Values File|Key Differences|
|-----|-------------|-----------------|
|Keycloak|`gitops/helm/keycloak/values/local.yaml`|Bundled PostgreSQL, nginx ingress, `keycloak.localhost`|
|Backstage|`gitops/helm/backstage/values/local.yaml`|Bundled PostgreSQL, guest auth, `backstage.localhost`|
|Kong|`gitops/helm/kong/values/local.yaml`|NodePort (30080/30443), no AWS annotations|
|Prometheus|`gitops/helm/kube-prometheus-stack/values/local.yaml`|No persistence, Grafana NodePort 30300|
|Loki|`gitops/helm/loki/values/local.yaml`|24h retention, filesystem storage|
|Fluent-Bit|`gitops/helm/fluent-bit/values/local.yaml`|Minimal resources|

## Local Secrets

Static secrets are defined in `gitops/kustomize/overlays/local/secrets.yaml`:

|Secret|Namespace|Purpose|
|--------|-----------|---------|
|`keycloak-admin-secret`|keycloak|Admin password: `localadmin123`|
|`keycloak-postgres-secret`|keycloak|PostgreSQL credentials|
|`backstage-postgres-secret`|backstage|PostgreSQL credentials|
|`backstage-secrets`|backstage|GitHub token, OIDC, DB connection|
|`kong-admin-secret`|kong|Admin API token|

> **Warning**: These are development-only credentials. Never use in production.

## Accessing Services

### Via Port Mappings (Kind extraPortMappings)

|Service|URL|
|---------|-----|
|Backstage|<http://localhost:7007>|
|Kong HTTP|<http://localhost:8090>|
|Kong HTTPS|<https://localhost:30443>|
|Grafana|<http://localhost:9000>|

### Via kubectl port-forward

```bash
# Keycloak
kubectl port-forward -n keycloak svc/keycloak 8080:80

# Backstage
kubectl port-forward -n backstage svc/backstage 7007:7007

# Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
```

### Via /etc/hosts (with ingress)

Add to `/etc/hosts`:

```text
127.0.0.1 keycloak.localhost backstage.localhost grafana.localhost
```

Then access via:

- <http://keycloak.localhost:8085>
- <http://backstage.localhost:8085>

## Resource Comparison

Local values use reduced resources for laptop-friendly operation:

|Component|AWS (dev)|Local|
|-----------|-----------|-------|
|Keycloak|250m/512Mi|100m/256Mi|
|Backstage|100m/256Mi|50m/128Mi|
|Prometheus|100m/512Mi|50m/256Mi|
|Grafana|50m/128Mi|25m/64Mi|

## Troubleshooting

### Pods pending due to resources

Reduce resource requests further or add more Kind worker nodes.

### Cannot pull images

Ensure Docker has sufficient resources allocated (recommended: 4 CPU, 8GB RAM).

### Services not accessible

1. Check Kind port mappings: `docker port ha-cluster-control-plane`
2. Verify services: `kubectl get svc -A`
3. Check pod status: `kubectl get pods -A`

### PostgreSQL not starting

Check PVC binding:

```bash
kubectl get pvc -A
```

For Kind, ensure `local-path-provisioner` is installed or use `emptyDir` for ephemeral storage.

## Cleanup

```bash
# Delete cluster
kind delete cluster --name ha-cluster

# Clean up local storage
rm -rf /tmp/local-path-provisioner/*
```

## Related Documentation

- [Tooling Apps Matrix](20_TOOLING_APPS_MATRIX.md) - Full list of platform apps and versions
- [Rebuild Sequence](06_REBUILD_SEQUENCE.md) - AWS cluster rebuild process
- [Teardown and Cleanup](15_TEARDOWN_AND_CLEANUP.md) - Destroying AWS resources
