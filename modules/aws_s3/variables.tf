variable "bucket_name" {
  type        = string
  description = "S3 bucket name."
}

variable "versioning_enabled" {
  type        = bool
  description = "Enable bucket versioning."
  default     = true
}

variable "encryption" {
  description = "Server-side encryption configuration."
  type = object({
    type          = string
    kms_key_alias = optional(string)
  })
  validation {
    condition     = contains(["SSE_S3", "SSE_KMS"], var.encryption.type)
    error_message = "encryption.type must be SSE_S3 or SSE_KMS."
  }
}

variable "public_access_block" {
  description = "Public access block configuration."
  type = object({
    block_public_acls       = bool
    block_public_policy     = bool
    ignore_public_acls      = bool
    restrict_public_buckets = bool
  })
}

variable "lifecycle_rules" {
  description = "Optional lifecycle rules."
  type = list(object({
    id      = string
    enabled = bool
    expiration = optional(object({
      days = number
    }))
    transition = optional(list(object({
      days          = number
      storage_class = string
    })))
  }))
  default = []
}

variable "logging" {
  description = "Access logging configuration."
  type = object({
    enabled       = bool
    target_bucket = optional(string)
    target_prefix = optional(string, "")
  })
  default = null
}

variable "tags" {
  type        = map(string)
  description = "Tags to apply to the bucket and related resources."
  default     = {}
}

variable "cost_alert" {
  description = "Optional cost alert configuration."
  type = object({
    threshold_gb = number
    alarm_name   = string
  })
  default = null
}

variable "force_destroy" {
  type        = bool
  description = "Force destroy bucket even if it contains objects."
  default     = false
}
