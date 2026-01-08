variable "role_name" {
  type        = string
  description = "Name for the Backstage IAM role."
  default     = "goldenpath-idp-backstage"
}

variable "namespace" {
  type        = string
  description = "Namespace where Backstage is deployed."
  default     = "backstage"
}

variable "service_account_name" {
  type        = string
  description = "Name of the Kubernetes service account for Backstage."
  default     = "backstage"
}

variable "oidc_provider_arn" {
  type        = string
  description = "ARN of the EKS OIDC provider."
}

variable "oidc_issuer_url" {
  type        = string
  description = "URL of the EKS OIDC issuer."
}

variable "enable_s3_techdocs" {
  type        = bool
  description = "Whether to enable S3 permissions for TechDocs."
  default     = false
}

variable "techdocs_bucket_name" {
  type        = string
  description = "Name of the S3 bucket for TechDocs."
  default     = ""
}

variable "tags" {
  type        = map(string)
  description = "Tags to apply to IAM resources."
  default     = {}
}
