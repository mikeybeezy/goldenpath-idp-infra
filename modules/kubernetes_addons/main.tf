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
  values = [var.argocd_values]

  set {
    name  = "server.service.type"
    value = "ClusterIP"
  }

  # Add common tags to the deployment if supported by the chart, or just track via Terraform state.
}

resource "helm_release" "aws_load_balancer_controller" {
  name       = "aws-load-balancer-controller"
  repository = "https://aws.github.io/eks-charts"
  chart      = "aws-load-balancer-controller"
  namespace  = "kube-system"
  wait       = true
  timeout    = 300

  set {
    name  = "clusterName"
    value = var.cluster_name
  }

  set {
    name  = "region"
    value = var.aws_region
  }

  set {
    name  = "vpcId"
    value = var.vpc_id
  }

  set {
    name  = "serviceAccount.create"
    value = "false"
  }

  set {
    name  = "serviceAccount.name"
    value = var.service_account_name
  }
}

resource "helm_release" "bootstrap_apps" {
  name             = "bootstrap-apps"
  chart            = "${path.module}/bootstrap-chart"
  version          = "0.1.0"
  namespace        = "argocd"
  create_namespace = true
  wait             = true
  timeout          = 300

  # Collect all YAML files from the target directory and pass them as a list of strings
  # Logic:
  # 1. Recursive discovery (**/*.{yaml,yml})
  # 2. Inject cluster name into cluster-autoscaler.yaml
  values = [
    yamlencode({
      manifests = [
        for f in(var.path_to_app_manifests != "" ? fileset(var.path_to_app_manifests, "**/*.{yaml,yml}") : []) :
        (
          basename(f) == "cluster-autoscaler.yaml" ?
          replace(
            file("${var.path_to_app_manifests}/${f}"),
            "        valueFiles:",
            "        parameters:\n          - name: autoDiscovery.clusterName\n            value: ${var.cluster_name}\n        valueFiles:"
          ) :
          file("${var.path_to_app_manifests}/${f}")
        )
      ]
    })
  ]

  depends_on = [
    helm_release.argocd,
    helm_release.aws_load_balancer_controller
  ]
}
