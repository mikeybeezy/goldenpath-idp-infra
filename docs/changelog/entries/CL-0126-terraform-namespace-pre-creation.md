# CL-0126: Terraform Namespace Pre-Creation

**Status**: Active
**Date**: 2026-01-13
**Type**: Feature
**Scope**: Kubernetes Add-ons Module
**Impact**: Bootstrap Process

## Summary

Added Terraform-managed namespace pre-creation to the `kubernetes_addons` module. All platform namespaces are now explicitly created via `kubernetes_namespace` resources before ArgoCD applications are deployed, preventing bootstrap failures due to missing namespaces.

## Changes

### New Resources

Created [modules/kubernetes_addons/namespaces.tf](../../modules/kubernetes_addons/namespaces.tf):
- `kubernetes_namespace.platform` - Creates 11 platform namespaces
- Namespaces include labels for classification and management
- Proper dependency ordering with ArgoCD installation

### Namespaces Created

The following namespaces are pre-created:

| Namespace | Purpose |
|-----------|---------|
| `argocd` | ArgoCD GitOps controller |
| `monitoring` | Prometheus, Grafana, Loki, Fluent Bit |
| `cert-manager` | Certificate management |
| `external-secrets` | External Secrets Operator |
| `backstage` | Backstage IDP |
| `kong-system` | Kong API Gateway |
| `datree-system` | Datree policy enforcement |
| `keycloak` | Keycloak IAM |
| `apps-stateful` | Stateful workload applications |
| `apps-sample-stateless` | Sample stateless applications |
| `apps-wordpress-efs` | WordPress with EFS storage |

### Modified Files

- [modules/kubernetes_addons/bootstrap_apps.tf](../../modules/kubernetes_addons/bootstrap_apps.tf): Added dependency on `kubernetes_namespace.platform`

## Problem Solved

### Before This Change

Bootstrap process could fail with:
```
Error: namespaces "cert-manager" not found
```

This occurred because:
1. ArgoCD Application CRDs are created in the `argocd` namespace
2. Applications reference destination namespaces that don't exist yet
3. Even though apps have `CreateNamespace=true`, the Application CRD creation fails first

### After This Change

- All namespaces exist before ArgoCD applications are deployed
- Terraform manages namespace lifecycle explicitly
- Works alongside ArgoCD's `CreateNamespace` sync option
- No bootstrap failures due to missing namespaces

## Deployment Order

The new deployment sequence:

```
1. EKS Cluster Created
2. ArgoCD Helm Release (creates argocd namespace via create_namespace=true)
3. AWS LB Controller + Metrics Server (parallel)
4. Platform Namespaces Created (kubernetes_namespace.platform)
5. ArgoCD Applications Deployed (bootstrap_apps)
6. Verification
```

## Rationale

### Why Terraform Instead of ArgoCD CreateNamespace?

1. **Explicit Control**: Terraform manages namespace lifecycle explicitly
2. **Labels and Annotations**: Add platform-specific metadata to namespaces
3. **Dependency Ordering**: Ensure namespaces exist before Application CRDs
4. **No Race Conditions**: Deterministic creation order
5. **GitOps Compatibility**: Works with ArgoCD's `CreateNamespace=true`

### Why Not Just Rely on ArgoCD?

ArgoCD's `CreateNamespace=true` creates namespaces when **syncing** applications, but:
- The Application CRD itself must be created first (in `argocd` namespace)
- If target namespace doesn't exist, Application CRD creation can fail
- Pre-creating avoids this race condition

## Migration Impact

### Existing Clusters

No impact - namespaces already exist. Terraform will import them on next apply:

```bash
# Terraform will show these as to be created, but they exist
# Use terraform import if needed
terraform import 'module.kubernetes_addons.kubernetes_namespace.platform["monitoring"]' monitoring
```

### New Clusters

Seamless - namespaces created before ArgoCD applications deploy.

## Testing

Validated with:
1. Fresh cluster build with build_id immutability enforcement
2. All 11 namespaces created successfully
3. ArgoCD applications deployed without namespace errors
4. No conflicts with ArgoCD's `CreateNamespace=true`

## References

- Commit: `51386839`
- Related: ArgoCD apps already have `CreateNamespace=true` in sync options
- Pattern follows: [ADR-0063: Platform Terraform Helm Bootstrap](../adrs/ADR-0063-platform-terraform-helm-bootstrap.md)

## Labels on Namespaces

Each namespace gets these labels:
```yaml
labels:
  app.kubernetes.io/managed-by: terraform
  goldenpath.idp/component: platform-bootstrap
  goldenpath.idp/namespace-type: platform
  name: <namespace-name>
```

## Future Enhancements

1. **Namespace Quotas**: Add resource quotas per namespace
2. **Network Policies**: Add default network policies per namespace
3. **RBAC**: Add default RBAC roles per namespace
4. **Cost Allocation**: Add cost center labels for FinOps
5. **Environment Separation**: Add environment-specific namespaces (dev/test/staging/prod)
