# Pre-create namespaces for ArgoCD applications
# This ensures namespaces exist before ArgoCD attempts to deploy applications
# Without this, ArgoCD applications may fail if syncOptions.CreateNamespace is not enabled

locals {
  # Core platform namespaces required by ArgoCD applications
  platform_namespaces = toset([
    "argocd",              # ArgoCD itself (also created by helm create_namespace)
    "monitoring",          # Prometheus, Grafana, Loki, Fluent Bit
    "cert-manager",        # Certificate management
    "external-secrets",    # External Secrets Operator
    "backstage",           # Backstage IDP
    "kong-system",         # Kong API Gateway
    "datree-system",       # Datree policy enforcement
    "keycloak",            # Keycloak IAM
    "apps-stateful",       # Stateful workload apps
    "apps-sample-stateless", # Sample stateless apps
    "apps-wordpress-efs",  # WordPress with EFS
  ])
}

resource "kubernetes_namespace" "platform" {
  for_each = local.platform_namespaces

  metadata {
    name = each.value

    labels = merge(
      local.common_labels,
      {
        "name"                         = each.value
        "goldenpath.idp/namespace-type" = "platform"
      }
    )

    annotations = {
      "terraform.io/managed" = "true"
    }
  }

  # Ensure namespaces are created after cluster is ready but before ArgoCD apps
  depends_on = [
    helm_release.argocd
  ]
}
