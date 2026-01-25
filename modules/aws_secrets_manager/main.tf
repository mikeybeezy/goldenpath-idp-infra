# -----------------------------------------------------------------------------
# Adopt-or-Create Pattern for Idempotent Secret Management
# -----------------------------------------------------------------------------
# When adopt_existing=true:
#   - First checks if secret exists using external data source
#   - If exists: adopts it (updates tags, returns existing ARN)
#   - If not exists: creates new secret
# This enables `make deploy` to succeed even when Terraform state is lost
# -----------------------------------------------------------------------------

# Use external data source to check existence (doesn't fail if not found)
data "external" "secret_check" {
  count = var.adopt_existing ? 1 : 0
  program = ["bash", "-c", <<-EOT
    secret=$(aws secretsmanager describe-secret --secret-id "${var.name}" --region "${data.aws_region.current.name}" 2>/dev/null || echo "")
    if [ -n "$secret" ]; then
      arn=$(echo "$secret" | jq -r '.ARN')
      deleted=$(echo "$secret" | jq -r '.DeletedDate // empty')
      restore_failed="false"
      if [ -n "$deleted" ]; then
        # Secret is scheduled for deletion - restore it
        if ! aws secretsmanager restore-secret --secret-id "${var.name}" --region "${data.aws_region.current.name}" >/dev/null 2>&1; then
          restore_failed="true"
        fi
      fi
      if [ "$restore_failed" = "true" ]; then
        echo "{\"exists\": \"false\", \"arn\": \"\", \"restore_failed\": \"true\"}"
      else
        echo "{\"exists\": \"true\", \"arn\": \"$arn\", \"restore_failed\": \"false\"}"
      fi
    else
      echo "{\"exists\": \"false\", \"arn\": \"\", \"restore_failed\": \"false\"}"
    fi
  EOT
  ]
}

data "aws_region" "current" {}

locals {
  # Check if we're adopting an existing secret
  secret_exists       = var.adopt_existing && length(data.external.secret_check) > 0 ? data.external.secret_check[0].result.exists == "true" : false
  restore_failed      = var.adopt_existing && length(data.external.secret_check) > 0 ? try(data.external.secret_check[0].result.restore_failed, "false") == "true" : false
  existing_secret_arn = local.secret_exists ? data.external.secret_check[0].result.arn : null
  should_create       = !local.secret_exists && !local.restore_failed

  # Plan-time determinable: will we have a secret ARN after apply?
  # Used for count expressions that can't depend on computed values
  will_have_secret = local.should_create || local.secret_exists

  # Compute the effective secret ARN (either created or existing)
  secret_arn = local.should_create ? (length(aws_secretsmanager_secret.this) > 0 ? aws_secretsmanager_secret.this[0].arn : null) : local.existing_secret_arn
  secret_id  = local.should_create ? (length(aws_secretsmanager_secret.this) > 0 ? aws_secretsmanager_secret.this[0].id : null) : local.existing_secret_arn

  # Compute tags to apply
  computed_tags = merge(
    var.tags,
    var.metadata != null ? {
      "goldenpath.idp/id"    = var.metadata.id
      "goldenpath.idp/owner" = var.metadata.owner
      "goldenpath.idp/risk"  = var.metadata.risk
    } : {}
  )
}

# -----------------------------------------------------------------------------
# Guard against scheduled-for-deletion secrets that could not be restored
# -----------------------------------------------------------------------------
resource "null_resource" "restore_guard" {
  count = local.restore_failed ? 1 : 0

  lifecycle {
    precondition {
      condition     = !local.restore_failed
      error_message = "Secret ${var.name} is scheduled for deletion and could not be restored. Ensure secretsmanager:RestoreSecret permissions or clear the deletion window before retrying."
    }
  }
}

# -----------------------------------------------------------------------------
# Create secret (only when not adopting existing)
# -----------------------------------------------------------------------------
resource "aws_secretsmanager_secret" "this" {
  count = local.should_create ? 1 : 0

  name        = var.name
  description = var.description
  kms_key_id  = var.kms_key_id
  tags        = local.computed_tags

  recovery_window_in_days = var.recovery_window_in_days
}

# -----------------------------------------------------------------------------
# Set initial value for new secrets (placeholder for required keys)
# -----------------------------------------------------------------------------
resource "aws_secretsmanager_secret_version" "initial" {
  count = local.should_create && var.initial_value != null ? 1 : 0

  secret_id     = aws_secretsmanager_secret.this[0].id
  secret_string = var.initial_value

  lifecycle {
    ignore_changes = [secret_string]
  }
}

# -----------------------------------------------------------------------------
# Update tags on adopted secret
# -----------------------------------------------------------------------------
resource "null_resource" "adopt_tags" {
  count = local.secret_exists ? 1 : 0

  triggers = {
    secret_arn = local.existing_secret_arn
    tags_hash  = sha256(jsonencode(local.computed_tags))
  }

  provisioner "local-exec" {
    command = <<-EOT
      aws secretsmanager tag-resource \
        --secret-id "${local.existing_secret_arn}" \
        --region "${data.aws_region.current.name}" \
        --tags '${jsonencode([for k, v in local.computed_tags : { Key = k, Value = v }])}'
    EOT
  }
}

# -----------------------------------------------------------------------------
# Resource Policy
# -----------------------------------------------------------------------------
locals {
  # Use explicit create_policy if set, otherwise fall back to checking principal lengths
  should_create_policy = var.create_policy != null ? var.create_policy : (length(var.read_principals) > 0 || length(var.write_principals) > 0 || length(var.break_glass_principals) > 0)
}

resource "aws_secretsmanager_secret_policy" "this" {
  # Use will_have_secret (plan-time determinable) instead of secret_arn != null (apply-time)
  count      = local.should_create_policy && local.will_have_secret ? 1 : 0
  secret_arn = local.secret_arn
  policy     = data.aws_iam_policy_document.this[0].json
}

data "aws_iam_policy_document" "this" {
  count = local.should_create_policy ? 1 : 0

  dynamic "statement" {
    for_each = length(var.read_principals) > 0 ? [1] : []
    content {
      sid    = "AllowRead"
      effect = "Allow"
      actions = [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ]
      resources = [local.secret_arn]
      principals {
        type        = "AWS"
        identifiers = var.read_principals
      }
    }
  }

  dynamic "statement" {
    for_each = length(var.write_principals) > 0 ? [1] : []
    content {
      sid    = "AllowWrite"
      effect = "Allow"
      actions = [
        "secretsmanager:PutSecretValue",
        "secretsmanager:UpdateSecret"
      ]
      resources = [local.secret_arn]
      principals {
        type        = "AWS"
        identifiers = var.write_principals
      }
    }
  }

  dynamic "statement" {
    for_each = length(var.break_glass_principals) > 0 ? [1] : []
    content {
      sid       = "AllowBreakGlass"
      effect    = "Allow"
      actions   = ["secretsmanager:*"]
      resources = [local.secret_arn]
      principals {
        type        = "AWS"
        identifiers = var.break_glass_principals
      }
    }
  }
}

# -----------------------------------------------------------------------------
# Secret Rotation
# -----------------------------------------------------------------------------
resource "aws_secretsmanager_secret_rotation" "this" {
  count = var.rotation_lambda_arn != null && local.secret_id != null ? 1 : 0

  secret_id           = local.secret_id
  rotation_lambda_arn = var.rotation_lambda_arn

  lifecycle {
    precondition {
      condition     = var.rotation_rules != null && try(var.rotation_rules.automatically_after_days, null) != null
      error_message = "If rotation_lambda_arn is set, rotation_rules.automatically_after_days must also be provided."
    }
  }

  rotation_rules {
    automatically_after_days = var.rotation_rules.automatically_after_days
  }
}
