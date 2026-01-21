################################################################################
# NOTE: cluster_role_name and node_group_role_name removed.
# EKS cluster and node group IAM roles are created by the EKS module
# (modules/aws_eks/main.tf). This IAM module only manages IRSA roles.
# See: session_capture/2026-01-20-persistent-cluster-deployment.md
################################################################################

variable "tags" {
  type        = map(string)
  description = "Tags to apply to IAM resources."
  default     = {}
}

variable "environment" {
  type        = string
  description = "Environment name for tagging."
  default     = ""
}

variable "oidc_role_name" {
  type        = string
  description = "Name for the IAM role assumed via the EKS OIDC provider."
}

variable "enable_oidc_role" {
  type        = bool
  description = "Whether to create the OIDC assume role."
  default     = false
}

variable "enable_autoscaler_role" {
  type        = bool
  description = "Whether to create the cluster autoscaler IRSA role."
  default     = false
}

variable "autoscaler_role_name" {
  type        = string
  description = "Name for the cluster autoscaler IAM role."
  default     = "goldenpath-idp-cluster-autoscaler"
}

variable "autoscaler_policy_arn" {
  type        = string
  description = "Existing IAM policy ARN for cluster autoscaler (when pre-created)."
  default     = ""
}

variable "autoscaler_service_account_namespace" {
  type        = string
  description = "Namespace for the cluster autoscaler service account."
  default     = "kube-system"
}

variable "autoscaler_service_account_name" {
  type        = string
  description = "Name of the cluster autoscaler service account."
  default     = "cluster-autoscaler"
}

variable "enable_lb_controller_role" {
  type        = bool
  description = "Whether to create the AWS Load Balancer Controller IRSA role."
  default     = false
}

variable "lb_controller_role_name" {
  type        = string
  description = "Name for the AWS Load Balancer Controller IAM role."
  default     = "goldenpath-idp-aws-load-balancer-controller"
}

variable "lb_controller_policy_arn" {
  type        = string
  description = "Existing IAM policy ARN for AWS Load Balancer Controller (when pre-created)."
  default     = ""
}

variable "lb_controller_service_account_namespace" {
  type        = string
  description = "Namespace for the AWS Load Balancer Controller service account."
  default     = "kube-system"
}

variable "lb_controller_service_account_name" {
  type        = string
  description = "Name of the AWS Load Balancer Controller service account."
  default     = "aws-load-balancer-controller"
}

variable "enable_eso_role" {
  type        = bool
  description = "Whether to create the External Secrets Operator IRSA role."
  default     = false
}

variable "eso_role_name" {
  type        = string
  description = "Name for the External Secrets Operator IAM role."
  default     = "goldenpath-idp-eso-role"
}

variable "eso_service_account_namespace" {
  type        = string
  description = "Namespace for the ESO service account."
  default     = "external-secrets"
}

variable "eso_service_account_name" {
  type        = string
  description = "Name of the ESO service account."
  default     = "external-secrets"
}

variable "enable_external_dns_role" {
  type        = bool
  description = "Whether to create the ExternalDNS IRSA role."
  default     = false
}

variable "external_dns_role_name" {
  type        = string
  description = "Name for the ExternalDNS IAM role."
  default     = "goldenpath-idp-external-dns"
}

variable "external_dns_policy_arn" {
  type        = string
  description = "Existing IAM policy ARN for ExternalDNS (when pre-created)."
  default     = ""
}

variable "external_dns_service_account_namespace" {
  type        = string
  description = "Namespace for the ExternalDNS service account."
  default     = "kube-system"
}

variable "external_dns_service_account_name" {
  type        = string
  description = "Name of the ExternalDNS service account."
  default     = "external-dns"
}

variable "external_dns_zone_id" {
  type        = string
  description = "Route53 hosted zone ID managed by ExternalDNS."
  default     = ""
  validation {
    condition     = var.enable_external_dns_role == false || var.external_dns_zone_id != ""
    error_message = "external_dns_zone_id must be set when enable_external_dns_role is true."
  }
}

variable "oidc_issuer_url" {
  type        = string
  description = "OIDC issuer URL for the EKS cluster."
}

variable "oidc_provider_arn" {
  type        = string
  description = "ARN of the IAM OIDC provider for the EKS cluster."
}

variable "oidc_audience" {
  type        = string
  description = "OIDC audience claim for the web identity token."
  default     = "sts.amazonaws.com"
}

variable "oidc_subject" {
  type        = string
  description = "OIDC subject claim allowed to assume the role."
}
