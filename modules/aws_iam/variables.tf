variable "cluster_role_name" {
  type        = string
  description = "Name for the EKS cluster IAM role."
}

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

variable "node_group_role_name" {
  type        = string
  description = "Name for the EKS node group IAM role."
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
