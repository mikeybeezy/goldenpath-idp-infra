resource "aws_secretsmanager_secret" "this" {
  name        = var.name
  description = var.description
  kms_key_id  = var.kms_key_id

  tags = merge(
    var.tags,
    var.metadata != null ? {
      "goldenpath.idp/id"    = var.metadata.id
      "goldenpath.idp/owner" = var.metadata.owner
      "goldenpath.idp/risk"  = var.metadata.risk
    } : {}
  )

  recovery_window_in_days = var.recovery_window_in_days
}

resource "aws_secretsmanager_secret_policy" "this" {
  count      = length(var.read_principals) > 0 || length(var.write_principals) > 0 || length(var.break_glass_principals) > 0 ? 1 : 0
  secret_arn = aws_secretsmanager_secret.this.arn
  policy     = data.aws_iam_policy_document.this[0].json
}

data "aws_iam_policy_document" "this" {
  count = length(var.read_principals) > 0 || length(var.write_principals) > 0 || length(var.break_glass_principals) > 0 ? 1 : 0

  dynamic "statement" {
    for_each = length(var.read_principals) > 0 ? [1] : []
    content {
      sid    = "AllowRead"
      effect = "Allow"
      actions = [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ]
      resources = [aws_secretsmanager_secret.this.arn]
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
      resources = [aws_secretsmanager_secret.this.arn]
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
      resources = [aws_secretsmanager_secret.this.arn]
      principals {
        type        = "AWS"
        identifiers = var.break_glass_principals
      }
    }
  }
}

resource "aws_secretsmanager_secret_rotation" "this" {
  count = var.rotation_lambda_arn != null ? 1 : 0

  secret_id           = aws_secretsmanager_secret.this.id
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
