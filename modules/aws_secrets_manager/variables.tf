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
  validation {
    condition     = var.recovery_window_in_days == 0 || (var.recovery_window_in_days >= 7 && var.recovery_window_in_days <= 30)
    error_message = "recovery_window_in_days must be 0 or between 7 and 30 for platform-governed secrets."
  }
}

variable "metadata" {
  description = "Governance metadata for the secret"
  type = object({
    id    = string
    owner = string
    risk  = optional(string, "medium")
  })
  default = null
  validation {
    condition     = var.metadata == null ? true : contains(["low", "medium", "high"], var.metadata.risk)
    error_message = "metadata.risk must be one of: low, medium, high."
  }
}

variable "rotation_lambda_arn" {
  description = "Specifies the ARN of the Lambda function that can rotate the secret."
  type        = string
  default     = null
}

variable "rotation_rules" {
  description = "A structure that defines the rotation configuration for the secret. Must be non-null when rotation_lambda_arn is set."
  type = object({
    automatically_after_days = number
  })
  default = null
  validation {
    condition = (
      var.rotation_lambda_arn == null
      ? var.rotation_rules == null
      : var.rotation_rules != null && var.rotation_rules.automatically_after_days >= 1
    )
    error_message = "rotation_rules must be null when rotation_lambda_arn is null; when rotation is enabled, set rotation_rules.automatically_after_days >= 1."
  }
}

variable "read_principals" {
  description = "List of ARNs allowed to read the secret"
  type        = list(string)
  default     = []
}

variable "write_principals" {
  description = "List of ARNs allowed to write/update the secret"
  type        = list(string)
  default     = []
}

variable "break_glass_principals" {
  description = "List of ARNs allowed for break-glass administrative access"
  type        = list(string)
  default     = []
}
