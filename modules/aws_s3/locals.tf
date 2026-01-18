locals {
  encryption_algorithm = var.encryption.type == "SSE_KMS" ? "aws:kms" : "AES256"
  kms_key_id           = var.encryption.type == "SSE_KMS" ? var.encryption.kms_key_alias : null
  logging_enabled      = var.logging != null && var.logging.enabled
  lifecycle_enabled    = length(var.lifecycle_rules) > 0
  cost_alert_enabled   = var.cost_alert != null
  cost_alert_bytes     = var.cost_alert != null ? var.cost_alert.threshold_gb * 1024 * 1024 * 1024 : 0
}
