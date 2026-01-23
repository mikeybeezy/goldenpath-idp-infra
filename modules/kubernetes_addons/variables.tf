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

# ADR-0179, ADR-0180: Bootstrap values for dynamic hostname generation
variable "bootstrap_values" {
  description = "Bootstrap values to inject into ArgoCD applications (global.hostSuffix, etc.)"
  type = object({
    host_suffix  = string
    dns_owner_id = string
    lifecycle    = string
    build_id     = string
    max_tier     = string
  })
  default = {
    host_suffix  = ""
    dns_owner_id = ""
    lifecycle    = "persistent"
    build_id     = ""
    max_tier     = "3"
  }
}
