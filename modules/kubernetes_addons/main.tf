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

resource "kubernetes_manifest" "applications" {
  for_each = var.path_to_app_manifests != "" ? fileset(var.path_to_app_manifests, "*.yaml") : []

  manifest = yamldecode(file("${var.path_to_app_manifests}/${each.value}"))

  depends_on = [
    helm_release.argocd
  ]
}
