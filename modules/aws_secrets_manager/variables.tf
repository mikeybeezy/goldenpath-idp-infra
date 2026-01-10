variable "name" {
  description = "The name of the secret"
  type        = string
}

variable "description" {
  description = "The description of the secret"
  type        = string
  default     = "Managed by Terraform"
}

variable "kms_key_id" {
  description = "The ARN or Id of the KMS key to use for encryption. If not specified, the default AWS account key is used."
  type        = string
  default     = null
}

variable "tags" {
  description = "A mapping of tags to assign to the secret"
  type        = map(string)
  default     = {}
}

variable "recovery_window_in_days" {
  description = "Number of days that AWS Secrets Manager waits before it can delete the secret."
  type        = number
  default     = 7
}

variable "metadata" {
  description = "Governance metadata for the secret"
  type = object({
    id    = string
    owner = string
    risk  = optional(string, "medium")
  })
  default = null
}
