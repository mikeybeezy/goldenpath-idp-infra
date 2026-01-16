################################################################################
# Platform RDS PostgreSQL Module
# Provisions a PostgreSQL RDS instance with configurable options
# Each component is a separate resource for independent lifecycle management
################################################################################

# -----------------------------------------------------------------------------
# DB Subnet Group
# -----------------------------------------------------------------------------
resource "aws_db_subnet_group" "this" {
  count = var.create_subnet_group ? 1 : 0

  name        = "${var.identifier}-subnet-group"
  description = "Subnet group for ${var.identifier} RDS instance"
  subnet_ids  = var.subnet_ids

  tags = merge(
    var.tags,
    {
      Name = "${var.identifier}-subnet-group"
    }
  )
}

# -----------------------------------------------------------------------------
# Security Group
# -----------------------------------------------------------------------------
resource "aws_security_group" "this" {
  count = var.create_security_group ? 1 : 0

  name        = "${var.identifier}-sg"
  description = "Security group for ${var.identifier} RDS instance"
  vpc_id      = var.vpc_id

  tags = merge(
    var.tags,
    {
      Name = "${var.identifier}-sg"
    }
  )

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group_rule" "ingress_cidr" {
  count = var.create_security_group && length(var.allowed_cidr_blocks) > 0 ? 1 : 0

  type              = "ingress"
  from_port         = 5432
  to_port           = 5432
  protocol          = "tcp"
  cidr_blocks       = var.allowed_cidr_blocks
  security_group_id = aws_security_group.this[0].id
  description       = "PostgreSQL from allowed CIDRs"
}

resource "aws_security_group_rule" "ingress_sg" {
  for_each = var.create_security_group ? toset(var.allowed_security_group_ids) : []

  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  source_security_group_id = each.value
  security_group_id        = aws_security_group.this[0].id
  description              = "PostgreSQL from ${each.value}"
}

resource "aws_security_group_rule" "egress" {
  count = var.create_security_group ? 1 : 0

  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.this[0].id
  description       = "All outbound traffic"
}

# -----------------------------------------------------------------------------
# Parameter Group
# -----------------------------------------------------------------------------
resource "aws_db_parameter_group" "this" {
  count = var.create_parameter_group ? 1 : 0

  name        = "${var.identifier}-params"
  family      = "postgres${var.engine_version_major}"
  description = "Parameter group for ${var.identifier}"

  dynamic "parameter" {
    for_each = var.db_parameters
    content {
      name         = parameter.value.name
      value        = parameter.value.value
      apply_method = lookup(parameter.value, "apply_method", "immediate")
    }
  }

  tags = var.tags

  lifecycle {
    create_before_destroy = true
  }
}

# -----------------------------------------------------------------------------
# Master Password Generation
# -----------------------------------------------------------------------------
resource "random_password" "master" {
  count = var.create_random_password ? 1 : 0

  length  = 32
  special = false
}

locals {
  master_password    = var.create_random_password ? random_password.master[0].result : var.master_password
  subnet_group_name  = var.create_subnet_group ? aws_db_subnet_group.this[0].name : var.existing_subnet_group_name
  security_group_ids = var.create_security_group ? [aws_security_group.this[0].id] : var.existing_security_group_ids
  parameter_group    = var.create_parameter_group ? aws_db_parameter_group.this[0].name : var.existing_parameter_group_name
}

# -----------------------------------------------------------------------------
# RDS Instance
# -----------------------------------------------------------------------------
resource "aws_db_instance" "this" {
  identifier = var.identifier

  # Engine
  engine               = "postgres"
  engine_version       = var.engine_version
  instance_class       = var.instance_class
  parameter_group_name = local.parameter_group

  # Storage
  allocated_storage     = var.allocated_storage
  max_allocated_storage = var.max_allocated_storage
  storage_type          = var.storage_type
  storage_encrypted     = var.storage_encrypted
  kms_key_id            = var.kms_key_id

  # Database
  db_name  = var.database_name
  username = var.master_username
  password = local.master_password
  port     = 5432

  # Network
  db_subnet_group_name   = local.subnet_group_name
  vpc_security_group_ids = local.security_group_ids
  publicly_accessible    = false
  multi_az               = var.multi_az

  # Backup & Maintenance
  backup_retention_period   = var.backup_retention_period
  backup_window             = var.backup_window
  maintenance_window        = var.maintenance_window
  copy_tags_to_snapshot     = true
  delete_automated_backups  = var.delete_automated_backups
  deletion_protection       = var.deletion_protection
  skip_final_snapshot       = var.skip_final_snapshot
  final_snapshot_identifier = var.skip_final_snapshot ? null : "${var.identifier}-final-${formatdate("YYYY-MM-DD", timestamp())}"

  # Monitoring
  performance_insights_enabled          = var.performance_insights_enabled
  performance_insights_retention_period = var.performance_insights_enabled ? var.performance_insights_retention_period : null
  enabled_cloudwatch_logs_exports       = var.enabled_cloudwatch_logs_exports

  # Lifecycle
  apply_immediately = var.apply_immediately

  tags = merge(
    var.tags,
    {
      Name = var.identifier
    }
  )

  lifecycle {
    ignore_changes = [
      final_snapshot_identifier
    ]
  }
}
