resource "aws_s3_bucket" "this" {
  bucket        = var.bucket_name
  force_destroy = var.force_destroy
  tags          = var.tags

  lifecycle {
    precondition {
      condition     = var.encryption.type != "SSE_KMS" || (var.encryption.kms_key_alias != null && var.encryption.kms_key_alias != "")
      error_message = "SSE_KMS encryption requires encryption.kms_key_alias to be set."
    }
    precondition {
      condition     = !local.logging_enabled || (var.logging.target_bucket != null && var.logging.target_bucket != "")
      error_message = "Access logging requires logging.target_bucket to be set."
    }
  }
}

resource "aws_s3_bucket_versioning" "this" {
  bucket = aws_s3_bucket.this.id

  versioning_configuration {
    status = var.versioning_enabled ? "Enabled" : "Suspended"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "this" {
  bucket = aws_s3_bucket.this.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = local.encryption_algorithm
      kms_master_key_id = local.kms_key_id
    }
  }
}

resource "aws_s3_bucket_public_access_block" "this" {
  bucket = aws_s3_bucket.this.id

  block_public_acls       = var.public_access_block.block_public_acls
  block_public_policy     = var.public_access_block.block_public_policy
  ignore_public_acls      = var.public_access_block.ignore_public_acls
  restrict_public_buckets = var.public_access_block.restrict_public_buckets
}

resource "aws_s3_bucket_lifecycle_configuration" "this" {
  count  = local.lifecycle_enabled ? 1 : 0
  bucket = aws_s3_bucket.this.id

  dynamic "rule" {
    for_each = var.lifecycle_rules
    content {
      id     = rule.value.id
      status = rule.value.enabled ? "Enabled" : "Disabled"

      dynamic "expiration" {
        for_each = rule.value.expiration != null ? [rule.value.expiration] : []
        content {
          days = expiration.value.days
        }
      }

      dynamic "transition" {
        for_each = rule.value.transition != null ? rule.value.transition : []
        content {
          days          = transition.value.days
          storage_class = transition.value.storage_class
        }
      }
    }
  }
}

resource "aws_s3_bucket_logging" "this" {
  count  = local.logging_enabled ? 1 : 0
  bucket = aws_s3_bucket.this.id

  target_bucket = var.logging.target_bucket
  target_prefix = var.logging.target_prefix
}

resource "aws_cloudwatch_metric_alarm" "cost_alert" {
  count               = local.cost_alert_enabled ? 1 : 0
  alarm_name          = var.cost_alert.alarm_name
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "BucketSizeBytes"
  namespace           = "AWS/S3"
  period              = 86400
  statistic           = "Average"
  threshold           = local.cost_alert_bytes
  treat_missing_data  = "notBreaching"
  tags                = var.tags

  dimensions = {
    BucketName  = var.bucket_name
    StorageType = "StandardStorage"
  }
}
