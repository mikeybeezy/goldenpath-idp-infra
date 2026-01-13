# ArgoCD Image Updater
# Automatically updates container images in ArgoCD Applications when new tags are pushed to ECR

resource "helm_release" "argocd_image_updater" {
  count = var.enable_image_updater ? 1 : 0

  name             = "argocd-image-updater"
  repository       = "https://argoproj.github.io/argo-helm"
  chart            = "argocd-image-updater"
  version          = var.argocd_image_updater_version
  namespace        = "argocd"
  create_namespace = false
  wait             = true
  timeout          = 300

  # Configuration for ECR integration
  set {
    name  = "config.registries[0].name"
    value = "ECR"
  }

  set {
    name  = "config.registries[0].api_url"
    value = "https://${local.ecr_account_id}.dkr.ecr.${var.aws_region}.amazonaws.com"
  }

  set {
    name  = "config.registries[0].prefix"
    value = "${local.ecr_account_id}.dkr.ecr.${var.aws_region}.amazonaws.com"
  }

  set {
    name  = "config.registries[0].credentials"
    value = "ext:/scripts/ecr-login.sh"
  }

  # Git write-back configuration (commits image updates to Git)
  set {
    name  = "config.git.user"
    value = "argocd-image-updater"
  }

  set {
    name  = "config.git.email"
    value = "argocd-image-updater@goldenpath-idp.local"
  }

  # Use IRSA for ECR authentication
  set {
    name  = "serviceAccount.create"
    value = var.create_image_updater_sa ? "true" : "false"
  }

  set {
    name  = "serviceAccount.name"
    value = var.image_updater_sa_name
  }

  set {
    name  = "serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn"
    value = var.image_updater_role_arn
  }

  # Log level for debugging
  set {
    name  = "config.logLevel"
    value = "info"
  }

  # Update interval (check for new images every 2 minutes)
  set {
    name  = "config.interval"
    value = "2m"
  }

  depends_on = [helm_release.argocd]
}
