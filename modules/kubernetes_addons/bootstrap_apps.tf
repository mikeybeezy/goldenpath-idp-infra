# Bootstrap ArgoCD Applications
# Deploys all ArgoCD Application manifests from gitops/argocd/apps/<env>/

locals {
  # Improved cluster name injection using regex replacement
  cluster_name_token = "$CLUSTER_NAME"
}

resource "helm_release" "bootstrap_apps" {
  name             = "bootstrap-apps"
  chart            = "${path.module}/bootstrap-chart"
  version          = "0.1.0"
  namespace        = "argocd"
  create_namespace = true
  wait             = true
  timeout          = 300

  # Collect all YAML files and inject cluster name dynamically
  values = [
    yamlencode({
      clusterName = var.cluster_name
      manifests = [
        for f in(var.path_to_app_manifests != "" ? fileset(var.path_to_app_manifests, "**/*.{yaml,yml}") : []) :
        replace(
          file("${var.path_to_app_manifests}/${f}"),
          local.cluster_name_token,
          var.cluster_name
        )
      ]
    })
  ]

  depends_on = [
    helm_release.argocd,
    helm_release.aws_load_balancer_controller,
    helm_release.metrics_server
  ]
}
