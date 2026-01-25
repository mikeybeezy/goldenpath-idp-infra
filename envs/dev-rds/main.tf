# AGENT_CONTEXT: Read .agent/README.md for rules
################################################################################
# Platform RDS - Standalone Bounded Context
#
# This is the persistent data layer for platform tooling applications.
# It is intentionally separated from the EKS cluster state to ensure:
# - Data survives cluster rebuilds
# - Deletion requires console intervention (not terraform destroy)
# - Clear separation of concerns between compute and data
#
# ADR Reference: ADR-0158-platform-standalone-rds-bounded-context.md
################################################################################

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  backend "s3" {
    # Backend config provided via -backend-config flags or init
    # State key: envs/dev-rds/terraform.tfstate
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = local.common_tags
  }
}

################################################################################
# Local Variables
################################################################################

locals {
  environment = var.environment
  identifier  = "${var.identifier_prefix}-${local.environment}"

  common_tags = {
    Environment = local.environment
    Project     = "goldenpath-idp"
    ManagedBy   = "terraform"
    Owner       = var.owner_team
    Component   = "platform-rds"
    CostCenter  = var.cost_center
    Application = "platform-database"
    # No BuildId tag - this is persistent infrastructure
  }
}

################################################################################
# Data Sources - VPC Discovery
# RDS needs to know the VPC but doesn't create it
################################################################################

data "aws_vpc" "platform" {
  filter {
    name   = "tag:Project"
    values = ["goldenpath-idp"]
  }

  filter {
    name   = "tag:Environment"
    values = [local.environment]
  }

  dynamic "filter" {
    for_each = var.vpc_name != null ? [var.vpc_name] : []
    content {
      name   = "tag:Name"
      values = [filter.value]
    }
  }
}

data "aws_subnets" "private" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.platform.id]
  }

  filter {
    name   = "tag:Name"
    values = ["*private*"]
  }
}

################################################################################
# DB Subnet Group
################################################################################

resource "aws_db_subnet_group" "platform" {
  name        = "${local.identifier}-subnet-group"
  description = "Subnet group for ${local.identifier} platform RDS"
  subnet_ids  = data.aws_subnets.private.ids

  tags = {
    Name = "${local.identifier}-subnet-group"
  }
}

################################################################################
# Security Group
################################################################################

resource "aws_security_group" "rds" {
  name        = "${local.identifier}-rds-sg"
  description = "Security group for ${local.identifier} platform RDS"
  vpc_id      = data.aws_vpc.platform.id

  tags = {
    Name = "${local.identifier}-rds-sg"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group_rule" "ingress_vpc" {
  type              = "ingress"
  from_port         = 5432
  to_port           = 5432
  protocol          = "tcp"
  cidr_blocks       = [data.aws_vpc.platform.cidr_block]
  security_group_id = aws_security_group.rds.id
  description       = "PostgreSQL from VPC CIDR"
}

resource "aws_security_group_rule" "egress_all" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.rds.id
  description       = "All outbound traffic"
}

################################################################################
# Parameter Group - SSL Required
################################################################################

resource "aws_db_parameter_group" "platform" {
  name        = "${local.identifier}-params"
  family      = "postgres${var.engine_version_major}"
  description = "Parameter group for ${local.identifier} - SSL required"

  # Force SSL connections
  parameter {
    name  = "rds.force_ssl"
    value = "1"
  }

  # Logging for debugging
  parameter {
    name  = "log_statement"
    value = "ddl"
  }

  parameter {
    name  = "log_min_duration_statement"
    value = "1000" # Log queries over 1 second
  }

  tags = {
    Name = "${local.identifier}-params"
  }

  lifecycle {
    create_before_destroy = true
  }
}

################################################################################
# Master Password Generation
################################################################################

resource "random_password" "master" {
  length  = 32
  special = false
}

################################################################################
# RDS Instance
################################################################################

resource "aws_db_instance" "platform" {
  identifier = local.identifier

  # Engine
  engine               = "postgres"
  engine_version       = var.engine_version
  instance_class       = var.instance_class
  parameter_group_name = aws_db_parameter_group.platform.name

  # Storage
  allocated_storage     = var.allocated_storage
  max_allocated_storage = var.max_allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true
  kms_key_id            = var.kms_key_id

  # Database
  db_name  = var.database_name
  username = var.master_username
  password = random_password.master.result
  port     = 5432

  # Network
  db_subnet_group_name   = aws_db_subnet_group.platform.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = false
  multi_az               = var.multi_az

  # Backup & Maintenance
  backup_retention_period   = var.backup_retention_period
  backup_window             = var.backup_window
  maintenance_window        = var.maintenance_window
  copy_tags_to_snapshot     = true
  delete_automated_backups  = false
  skip_final_snapshot       = false
  final_snapshot_identifier = "${local.identifier}-final-snapshot"

  # CRITICAL: Deletion Protection
  deletion_protection = true

  # Monitoring
  performance_insights_enabled          = true
  performance_insights_retention_period = var.performance_insights_retention_period
  enabled_cloudwatch_logs_exports       = ["postgresql", "upgrade"]

  # Apply changes immediately in dev, use maintenance window in prod
  apply_immediately = var.apply_immediately

  tags = {
    Name = local.identifier
  }

  # CRITICAL: Prevent accidental destruction
  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      final_snapshot_identifier
    ]
  }
}

################################################################################
# Master Credentials Secret
################################################################################

resource "aws_secretsmanager_secret" "master" {
  name        = "goldenpath/${local.environment}/rds/master"
  description = "Master credentials for ${local.identifier} platform RDS"

  tags = {
    Name = "goldenpath/${local.environment}/rds/master"
  }
}

resource "aws_secretsmanager_secret_version" "master" {
  secret_id = aws_secretsmanager_secret.master.id
  secret_string = jsonencode({
    username             = var.master_username
    password             = random_password.master.result
    host                 = aws_db_instance.platform.address
    port                 = tostring(aws_db_instance.platform.port)
    dbname               = var.database_name
    engine               = "postgres"
    dbInstanceIdentifier = aws_db_instance.platform.identifier
  })
}

################################################################################
# Application Database Credentials
################################################################################

resource "random_password" "app" {
  for_each = var.application_databases

  length  = 32
  special = false
}

resource "aws_secretsmanager_secret" "app" {
  for_each = var.application_databases

  name        = "goldenpath/${local.environment}/${each.key}/postgres"
  description = "Database credentials for ${each.key} application"

  tags = {
    Name        = "goldenpath/${local.environment}/${each.key}/postgres"
    Application = each.key
  }
}

resource "aws_secretsmanager_secret_version" "app" {
  for_each = var.application_databases

  secret_id = aws_secretsmanager_secret.app[each.key].id
  secret_string = jsonencode({
    username = each.value.username
    password = random_password.app[each.key].result
    host     = aws_db_instance.platform.address
    port     = tostring(aws_db_instance.platform.port)
    dbname   = each.value.database_name
    engine   = "postgres"
    # Standard connection string fields only - no redundant password aliases
  })
}

################################################################################
# Secret Rotation
#
# V1: Manual rotation with CI enforcement (scheduled alerts + PR warnings)
# V1.1: Automated Lambda-based rotation
#
# Manual rotation is enforced via:
# - Daily scheduled GitHub workflow that alerts if secrets > 25 days old
# - PR gate that warns (non-blocking) if secrets are approaching rotation deadline
# - Runbook RB-0029 documents the manual rotation procedure
#
# See: .github/workflows/secret-rotation-check.yml
################################################################################

# Track secret creation date via tags for rotation monitoring
# The GitHub workflow checks secret age and alerts when rotation is due

################################################################################
# CloudWatch Alarms
################################################################################

resource "aws_cloudwatch_metric_alarm" "cpu_warning" {
  alarm_name          = "${local.identifier}-cpu-warning"
  alarm_description   = "RDS CPU utilization warning - ${local.identifier}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 70
  alarm_actions       = var.alarm_sns_topic_arn != "" ? [var.alarm_sns_topic_arn] : []
  ok_actions          = var.alarm_sns_topic_arn != "" ? [var.alarm_sns_topic_arn] : []

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.platform.identifier
  }

  tags = {
    Name     = "${local.identifier}-cpu-warning"
    Severity = "warning"
  }
}

resource "aws_cloudwatch_metric_alarm" "cpu_critical" {
  alarm_name          = "${local.identifier}-cpu-critical"
  alarm_description   = "RDS CPU utilization critical - ${local.identifier}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 90
  alarm_actions       = var.alarm_sns_topic_arn != "" ? [var.alarm_sns_topic_arn] : []
  ok_actions          = var.alarm_sns_topic_arn != "" ? [var.alarm_sns_topic_arn] : []

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.platform.identifier
  }

  tags = {
    Name     = "${local.identifier}-cpu-critical"
    Severity = "critical"
  }
}

resource "aws_cloudwatch_metric_alarm" "memory_warning" {
  alarm_name          = "${local.identifier}-memory-warning"
  alarm_description   = "RDS freeable memory warning - ${local.identifier}"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 2
  metric_name         = "FreeableMemory"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 536870912 # 512MB in bytes
  alarm_actions       = var.alarm_sns_topic_arn != "" ? [var.alarm_sns_topic_arn] : []
  ok_actions          = var.alarm_sns_topic_arn != "" ? [var.alarm_sns_topic_arn] : []

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.platform.identifier
  }

  tags = {
    Name     = "${local.identifier}-memory-warning"
    Severity = "warning"
  }
}

resource "aws_cloudwatch_metric_alarm" "memory_critical" {
  alarm_name          = "${local.identifier}-memory-critical"
  alarm_description   = "RDS freeable memory critical - ${local.identifier}"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 2
  metric_name         = "FreeableMemory"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 268435456 # 256MB in bytes
  alarm_actions       = var.alarm_sns_topic_arn != "" ? [var.alarm_sns_topic_arn] : []
  ok_actions          = var.alarm_sns_topic_arn != "" ? [var.alarm_sns_topic_arn] : []

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.platform.identifier
  }

  tags = {
    Name     = "${local.identifier}-memory-critical"
    Severity = "critical"
  }
}

resource "aws_cloudwatch_metric_alarm" "storage_warning" {
  alarm_name          = "${local.identifier}-storage-warning"
  alarm_description   = "RDS free storage space warning - ${local.identifier}"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 2
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  # 30% of allocated storage
  threshold     = var.allocated_storage * 1073741824 * 0.3
  alarm_actions = var.alarm_sns_topic_arn != "" ? [var.alarm_sns_topic_arn] : []
  ok_actions    = var.alarm_sns_topic_arn != "" ? [var.alarm_sns_topic_arn] : []

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.platform.identifier
  }

  tags = {
    Name     = "${local.identifier}-storage-warning"
    Severity = "warning"
  }
}

resource "aws_cloudwatch_metric_alarm" "storage_critical" {
  alarm_name          = "${local.identifier}-storage-critical"
  alarm_description   = "RDS free storage space critical - ${local.identifier}"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 2
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  # 15% of allocated storage
  threshold     = var.allocated_storage * 1073741824 * 0.15
  alarm_actions = var.alarm_sns_topic_arn != "" ? [var.alarm_sns_topic_arn] : []
  ok_actions    = var.alarm_sns_topic_arn != "" ? [var.alarm_sns_topic_arn] : []

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.platform.identifier
  }

  tags = {
    Name     = "${local.identifier}-storage-critical"
    Severity = "critical"
  }
}

resource "aws_cloudwatch_metric_alarm" "connections_warning" {
  alarm_name          = "${local.identifier}-connections-warning"
  alarm_description   = "RDS database connections warning - ${local.identifier}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = var.max_connections * 0.7
  alarm_actions       = var.alarm_sns_topic_arn != "" ? [var.alarm_sns_topic_arn] : []
  ok_actions          = var.alarm_sns_topic_arn != "" ? [var.alarm_sns_topic_arn] : []

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.platform.identifier
  }

  tags = {
    Name     = "${local.identifier}-connections-warning"
    Severity = "warning"
  }
}

resource "aws_cloudwatch_metric_alarm" "read_latency_warning" {
  alarm_name          = "${local.identifier}-read-latency-warning"
  alarm_description   = "RDS read latency warning - ${local.identifier}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "ReadLatency"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 0.05 # 50ms
  alarm_actions       = var.alarm_sns_topic_arn != "" ? [var.alarm_sns_topic_arn] : []
  ok_actions          = var.alarm_sns_topic_arn != "" ? [var.alarm_sns_topic_arn] : []

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.platform.identifier
  }

  tags = {
    Name     = "${local.identifier}-read-latency-warning"
    Severity = "warning"
  }
}

resource "aws_cloudwatch_metric_alarm" "write_latency_warning" {
  alarm_name          = "${local.identifier}-write-latency-warning"
  alarm_description   = "RDS write latency warning - ${local.identifier}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "WriteLatency"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 0.05 # 50ms
  alarm_actions       = var.alarm_sns_topic_arn != "" ? [var.alarm_sns_topic_arn] : []
  ok_actions          = var.alarm_sns_topic_arn != "" ? [var.alarm_sns_topic_arn] : []

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.platform.identifier
  }

  tags = {
    Name     = "${local.identifier}-write-latency-warning"
    Severity = "warning"
  }
}
