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

resource "aws_secretsmanager_secret_rotation" "this" {
  count = var.rotation_lambda_arn != null ? 1 : 0

  secret_id           = aws_secretsmanager_secret.this.id
  rotation_lambda_arn = var.rotation_lambda_arn

  rotation_rules {
    automatically_after_days = var.rotation_rules.automatically_after_days
  }
}
