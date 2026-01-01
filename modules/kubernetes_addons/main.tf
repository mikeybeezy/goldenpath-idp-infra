resource "helm_release" "argocd" {
  name             = "argocd"
  repository       = "https://argoproj.github.io/argo-helm"
  chart            = "argo-cd"
  version          = var.argocd_version
  namespace        = "argocd"
  create_namespace = true
  wait             = true
  timeout          = 600

  # Pass minimal values or rely on defaults.
  # We use "server.insecure=true" if we are terminating TLS at an oversized ALB (common in simple setups),
  # but here we stick to defaults unless specified.
  set {
    name  = "server.service.type"
    value = "ClusterIP"
  }

  # Add common tags to the deployment if supported by the chart, or just track via Terraform state.
}
