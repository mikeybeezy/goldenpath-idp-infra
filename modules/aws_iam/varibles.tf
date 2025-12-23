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
