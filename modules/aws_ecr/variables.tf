variable "name" {
  type        = string
  description = "Name of the ECR repository."
}

variable "tags" {
  type        = map(string)
  description = "Tags to apply to the repository."
  default     = {}
}

variable "environment" {
  type        = string
  description = "Environment name for tagging."
  default     = ""
}

variable "metadata" {
  type = object({
    id          = string
    owner       = string
    description = optional(string, "")
    risk        = optional(string, "medium")
  })
  description = "Governance lifecycle metadata for the repository."
  default     = null
}

variable "image_tag_mutability" {
  type        = string
  description = "The tag mutability setting for the repository. Must be one of: MUTABLE or IMMUTABLE."
  default     = "MUTABLE"
}

variable "scan_on_push" {
  type        = bool
  description = "Indicates whether images are scanned after being pushed to the repository."
  default     = true
}

variable "encryption_type" {
  type        = string
  description = "The encryption type to use for the repository. Valid values are AES256 or KMS."
  default     = "AES256"
}

variable "kms_key" {
  type        = string
  description = "The ARN of the KMS key to use when encryption_type is KMS. If not specified, uses the default AWS managed key for ECR."
  default     = null
}

variable "force_delete" {
  type        = bool
  description = "If true, will delete the repository even if it contains images. Defaults to false."
  default     = false
}

variable "enable_lifecycle_policy" {
  type        = bool
  description = "Whether to enable the default lifecycle policy (keep last N images)."
  default     = true
}

variable "lifecycle_policy_keep_image_count" {
  type        = number
  description = "Number of recent images to keep when using the default lifecycle policy."
  default     = 30
}
