# ArgoCD GitOps Controller Installation
# This deploys ArgoCD via Helm to enable GitOps-based application management

resource "helm_release" "argocd" {
  name             = "argocd"
  repository       = "https://argoproj.github.io/argo-helm"
  chart            = "argo-cd"
  version          = var.argocd_version
  namespace        = "argocd"
  create_namespace = true
  wait             = true
  timeout          = 600

  # Custom values from gitops/helm/argocd/values/<env>.yaml
  values = var.argocd_values != "" ? [var.argocd_values] : []

  # Ensure server is ClusterIP (internal-only by default)
  set {
    name  = "server.service.type"
    value = "ClusterIP"
  }

  # Enable ArgoCD Image Updater integration
  set {
    name  = "configs.cm.application.resourceTrackingMethod"
    value = "annotation"
  }
}

# ArgoCD admin password (retrieve after installation)
data "kubernetes_secret" "argocd_admin" {
  metadata {
    name      = "argocd-initial-admin-secret"
    namespace = "argocd"
  }

  depends_on = [helm_release.argocd]
}
