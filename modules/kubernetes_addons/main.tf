terraform {
  required_providers {
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.12"
    }
  }
}

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

  # ArgoCD creates Services/Ingresses that get intercepted by the LBC webhook.
  # LBC must be fully deployed first or the webhook has no endpoints.
  # See: session_capture/2026-01-23-v1-milestone-ephemeral-deploy-success.md
  depends_on = [helm_release.aws_load_balancer_controller]
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
  # 3. Inject global.hostSuffix into backstage.yaml (ADR-0179)
  # 4. Inject domainFilters override into external-dns.yaml (ADR-0178)
  values = [
    yamlencode({
      manifests = [
        for f in(var.path_to_app_manifests != "" ? fileset(var.path_to_app_manifests, "**/*.{yaml,yml}") : []) :
        (
          # cluster-autoscaler: inject clusterName (multi-source format uses 8-space indent)
          basename(f) == "cluster-autoscaler.yaml" ?
          replace(
            file("${var.path_to_app_manifests}/${f}"),
            "      helm:\n        valueFiles:",
            "      helm:\n        parameters:\n          - name: autoDiscovery.clusterName\n            value: ${var.cluster_name}\n        valueFiles:"
          ) :
          # backstage: inject global.hostSuffix for dynamic hostname (ADR-0179)
          basename(f) == "backstage.yaml" && var.bootstrap_values.host_suffix != "" ?
          replace(
            file("${var.path_to_app_manifests}/${f}"),
            "      helm:\n        valueFiles:",
            "      helm:\n        parameters:\n          - name: global.hostSuffix\n            value: ${var.bootstrap_values.host_suffix}\n        valueFiles:"
          ) :
          # external-dns: inject txtOwnerId for DNS ownership scoping (ADR-0178)
          # NOTE: domainFilters is NOT injected here - it MUST use the apex domain (goldenpathidp.io)
          # not the subdomain (dev.goldenpathidp.io). The correct value is in values/dev.yaml.
          basename(f) == "external-dns.yaml" && var.bootstrap_values.dns_owner_id != "" ?
          replace(
            file("${var.path_to_app_manifests}/${f}"),
            "        valueFiles:",
            "        parameters:\n          - name: txtOwnerId\n            value: ${var.bootstrap_values.dns_owner_id}\n        valueFiles:"
          ) :
          file("${var.path_to_app_manifests}/${f}")
        )
        if basename(f) != "metadata.yaml"
      ]
    })
  ]

  depends_on = [
    helm_release.argocd,
    helm_release.aws_load_balancer_controller
  ]
}
