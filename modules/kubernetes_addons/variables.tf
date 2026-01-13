variable "argocd_version" {
  description = "Version of the ArgoCD Helm chart to install."
  type        = string
  default     = "5.46.7" # Pinned stable version
}

variable "path_to_app_manifests" {
  description = "Path to the directory containing ArgoCD Application manifests (YAMLs) to verify/bootstrap."
  type        = string
  default     = ""
}

variable "tags" {
  description = "A map of tags to add to all resources."
  type        = map(string)
  default     = {}
}

variable "argocd_values" {
  description = "Custom values.yaml content for ArgoCD."
  type        = string
  default     = ""
}

variable "vpc_id" {
  description = "VPC ID where the cluster is running (required for AWS LB Controller)."
  type        = string
}

variable "cluster_name" {
  description = "Name of the EKS cluster (required for AWS LB Controller)."
  type        = string
}

variable "aws_region" {
  description = "AWS Region where the cluster is running (required for AWS LB Controller)."
  type        = string
}

variable "service_account_name" {
  description = "Name of the service account for AWS LB Controller."
  type        = string
  default     = "aws-load-balancer-controller"
}

variable "argocd_image_updater_version" {
  description = "Version of the ArgoCD Image Updater Helm chart to install."
  type        = string
  default     = "0.9.6" # Pinned stable version
}

variable "enable_image_updater" {
  description = "Whether to install ArgoCD Image Updater."
  type        = bool
  default     = true
}

variable "ecr_registry_id" {
  description = "AWS Account ID for ECR registry (required for Image Updater)."
  type        = string
  default     = ""
}

variable "create_image_updater_sa" {
  description = "Whether to create service account for Image Updater (false if created via Terraform kubernetes_service_account)."
  type        = bool
  default     = false
}

variable "image_updater_sa_name" {
  description = "Name of the service account for ArgoCD Image Updater."
  type        = string
  default     = "argocd-image-updater"
}

variable "image_updater_role_arn" {
  description = "IAM role ARN for ArgoCD Image Updater to access ECR (IRSA)."
  type        = string
  default     = ""
}

variable "metrics_server_version" {
  description = "Version of the Metrics Server Helm chart to install."
  type        = string
  default     = "3.11.0"
}

variable "enable_metrics_server" {
  description = "Whether to install Metrics Server."
  type        = bool
  default     = true
}

variable "enable_post_deployment_verification" {
  description = "Whether to run post-deployment verification checks (waits for critical apps)."
  type        = bool
  default     = true
}
