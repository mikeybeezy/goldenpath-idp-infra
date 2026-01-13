# Outputs for kubernetes_addons module

output "argocd_namespace" {
  description = "Namespace where ArgoCD is installed"
  value       = helm_release.argocd.namespace
}

output "argocd_release_name" {
  description = "Helm release name for ArgoCD"
  value       = helm_release.argocd.name
}

output "argocd_helm_release_status" {
  description = "Status of the ArgoCD Helm release"
  value       = helm_release.argocd.status
}

output "argocd_helm_release_version" {
  description = "Version of the ArgoCD Helm chart installed"
  value       = helm_release.argocd.version
}

output "argocd_admin_secret_name" {
  description = "Name of the Kubernetes secret containing ArgoCD admin password"
  value       = "argocd-initial-admin-secret"
}

output "argocd_server_service" {
  description = "ArgoCD server service name"
  value       = "argocd-server"
}

output "lb_controller_release_name" {
  description = "Helm release name for AWS Load Balancer Controller"
  value       = helm_release.aws_load_balancer_controller.name
}

output "metrics_server_installed" {
  description = "Whether Metrics Server was installed"
  value       = var.enable_metrics_server
}

output "image_updater_installed" {
  description = "Whether ArgoCD Image Updater was installed"
  value       = var.enable_image_updater
}

output "bootstrap_apps_release_name" {
  description = "Helm release name for bootstrap applications"
  value       = helm_release.bootstrap_apps.name
}

output "ecr_account_id" {
  description = "AWS Account ID used for ECR registry"
  value       = local.ecr_account_id
}
