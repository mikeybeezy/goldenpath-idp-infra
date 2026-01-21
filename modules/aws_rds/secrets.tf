################################################################################
# RDS Secrets Management
# Stores database credentials in AWS Secrets Manager
# These are separate resources for independent lifecycle management
################################################################################

# -----------------------------------------------------------------------------
# Master Credentials Secret
# -----------------------------------------------------------------------------
resource "aws_secretsmanager_secret" "master" {
  count = var.create_master_secret ? 1 : 0

  name                    = var.master_secret_name
  description             = "Master credentials for ${var.identifier} RDS instance"
  recovery_window_in_days = var.secret_recovery_window_in_days

  tags = var.tags
}

resource "aws_secretsmanager_secret_version" "master" {
  count = var.create_master_secret ? 1 : 0

  secret_id = aws_secretsmanager_secret.master[0].id
  secret_string = jsonencode({
    username          = var.master_username
    password          = local.master_password
    host              = aws_db_instance.this.address
    port              = tostring(aws_db_instance.this.port)
    dbname            = var.database_name
    engine            = "postgres"
    postgres-password = local.master_password
  })
}

# -----------------------------------------------------------------------------
# Application Database Secrets
# Each application gets its own secret with generated credentials
# -----------------------------------------------------------------------------
resource "random_password" "app" {
  for_each = var.application_databases

  length  = 32
  special = false
}

resource "aws_secretsmanager_secret" "app" {
  for_each = var.application_databases

  name                    = each.value.secret_name
  description             = "Database credentials for ${each.key} application"
  recovery_window_in_days = var.secret_recovery_window_in_days

  tags = var.tags
}

resource "aws_secretsmanager_secret_version" "app" {
  for_each = var.application_databases

  secret_id = aws_secretsmanager_secret.app[each.key].id
  secret_string = jsonencode({
    username          = each.value.username
    password          = random_password.app[each.key].result
    host              = aws_db_instance.this.address
    port              = tostring(aws_db_instance.this.port)
    dbname            = each.value.database_name
    engine            = "postgres"
    postgres-password = random_password.app[each.key].result
    admin-password    = random_password.app[each.key].result
  })
}
