# ---
# id: TFTEST-RDS-001
# type: terraform-test
# owner: platform-team
# status: active
# maturity: 1
# ---
# Terraform native tests for aws_rds module
# Run with: cd modules/aws_rds && terraform init && terraform test

# -----------------------------------------------------------------------------
# Mock Provider Configuration
# -----------------------------------------------------------------------------
mock_provider "aws" {}
mock_provider "random" {}

# -----------------------------------------------------------------------------
# Variables Block - Shared test inputs
# -----------------------------------------------------------------------------
variables {
  identifier = "test-db"
  vpc_id     = "vpc-12345678"
  subnet_ids = ["subnet-aaaaaaaa", "subnet-bbbbbbbb"]

  engine_version       = "15.4"
  engine_version_major = "15"
  instance_class       = "db.t3.micro"

  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp3"
  storage_encrypted     = true

  database_name   = "testdb"
  master_username = "testuser"

  backup_retention_period = 7
  multi_az                = false
  deletion_protection     = false

  tags = {
    Project   = "goldenpath-idp"
    ManagedBy = "terraform"
  }
}

# -----------------------------------------------------------------------------
# Test: RDS Instance Configuration
# -----------------------------------------------------------------------------
run "rds_instance_identifier" {
  command = plan

  assert {
    condition     = aws_db_instance.this.identifier == var.identifier
    error_message = "RDS instance identifier should match var.identifier"
  }

  assert {
    condition     = aws_db_instance.this.engine == "postgres"
    error_message = "RDS engine should be postgres"
  }

  assert {
    condition     = aws_db_instance.this.engine_version == var.engine_version
    error_message = "RDS engine version should match var.engine_version"
  }
}

# -----------------------------------------------------------------------------
# Test: Storage Configuration
# -----------------------------------------------------------------------------
run "storage_configuration" {
  command = plan

  assert {
    condition     = aws_db_instance.this.allocated_storage == var.allocated_storage
    error_message = "Allocated storage should match configuration"
  }

  assert {
    condition     = aws_db_instance.this.max_allocated_storage == var.max_allocated_storage
    error_message = "Max allocated storage should match configuration"
  }

  assert {
    condition     = aws_db_instance.this.storage_type == var.storage_type
    error_message = "Storage type should match configuration"
  }

  assert {
    condition     = aws_db_instance.this.storage_encrypted == true
    error_message = "Storage encryption should be enabled"
  }
}

# -----------------------------------------------------------------------------
# Test: Database Configuration
# -----------------------------------------------------------------------------
run "database_configuration" {
  command = plan

  assert {
    condition     = aws_db_instance.this.db_name == var.database_name
    error_message = "Database name should match configuration"
  }

  assert {
    condition     = aws_db_instance.this.username == var.master_username
    error_message = "Master username should match configuration"
  }

  assert {
    condition     = aws_db_instance.this.port == 5432
    error_message = "PostgreSQL port should be 5432"
  }
}

# -----------------------------------------------------------------------------
# Test: Network Security - Instance Not Publicly Accessible
# -----------------------------------------------------------------------------
run "not_publicly_accessible" {
  command = plan

  assert {
    condition     = aws_db_instance.this.publicly_accessible == false
    error_message = "RDS instance should NOT be publicly accessible"
  }
}

# -----------------------------------------------------------------------------
# Test: Backup Configuration
# -----------------------------------------------------------------------------
run "backup_configuration" {
  command = plan

  assert {
    condition     = aws_db_instance.this.backup_retention_period == var.backup_retention_period
    error_message = "Backup retention period should match configuration"
  }

  assert {
    condition     = aws_db_instance.this.copy_tags_to_snapshot == true
    error_message = "Tags should be copied to snapshots"
  }
}

# -----------------------------------------------------------------------------
# Test: Subnet Group Creation
# -----------------------------------------------------------------------------
run "subnet_group_created" {
  command = plan

  assert {
    condition     = length(aws_db_subnet_group.this) == 1
    error_message = "Subnet group should be created when create_subnet_group is true (default)"
  }

  assert {
    condition     = aws_db_subnet_group.this[0].name == "${var.identifier}-subnet-group"
    error_message = "Subnet group should be named '{identifier}-subnet-group'"
  }
}

# -----------------------------------------------------------------------------
# Test: Security Group Creation
# -----------------------------------------------------------------------------
run "security_group_created" {
  command = plan

  assert {
    condition     = length(aws_security_group.this) == 1
    error_message = "Security group should be created when create_security_group is true (default)"
  }

  assert {
    condition     = aws_security_group.this[0].name == "${var.identifier}-sg"
    error_message = "Security group should be named '{identifier}-sg'"
  }

  assert {
    condition     = aws_security_group.this[0].vpc_id == var.vpc_id
    error_message = "Security group should be in the specified VPC"
  }
}

# -----------------------------------------------------------------------------
# Test: Parameter Group Creation
# -----------------------------------------------------------------------------
run "parameter_group_created" {
  command = plan

  assert {
    condition     = length(aws_db_parameter_group.this) == 1
    error_message = "Parameter group should be created when create_parameter_group is true (default)"
  }

  assert {
    condition     = aws_db_parameter_group.this[0].family == "postgres${var.engine_version_major}"
    error_message = "Parameter group family should match postgres version"
  }
}

# -----------------------------------------------------------------------------
# Test: Random Password Generation
# -----------------------------------------------------------------------------
run "random_password_generated" {
  command = plan

  assert {
    condition     = length(random_password.master) == 1
    error_message = "Random password should be generated when create_random_password is true (default)"
  }

  assert {
    condition     = random_password.master[0].length == 32
    error_message = "Generated password should be 32 characters"
  }

  assert {
    condition     = random_password.master[0].special == false
    error_message = "Generated password should not include special characters"
  }
}

# -----------------------------------------------------------------------------
# Test: Skip Subnet Group When Disabled
# -----------------------------------------------------------------------------
run "skip_subnet_group_when_disabled" {
  command = plan

  variables {
    create_subnet_group        = false
    existing_subnet_group_name = "existing-subnet-group"
  }

  assert {
    condition     = length(aws_db_subnet_group.this) == 0
    error_message = "Subnet group should NOT be created when create_subnet_group is false"
  }
}

# -----------------------------------------------------------------------------
# Test: Skip Security Group When Disabled
# -----------------------------------------------------------------------------
run "skip_security_group_when_disabled" {
  command = plan

  variables {
    create_security_group       = false
    existing_security_group_ids = ["sg-existing123"]
  }

  assert {
    condition     = length(aws_security_group.this) == 0
    error_message = "Security group should NOT be created when create_security_group is false"
  }
}

# -----------------------------------------------------------------------------
# Test: Multi-AZ Configuration
# -----------------------------------------------------------------------------
run "multi_az_disabled_by_default" {
  command = plan

  assert {
    condition     = aws_db_instance.this.multi_az == false
    error_message = "Multi-AZ should be disabled by default"
  }
}

run "multi_az_when_enabled" {
  command = plan

  variables {
    multi_az = true
  }

  assert {
    condition     = aws_db_instance.this.multi_az == true
    error_message = "Multi-AZ should be enabled when configured"
  }
}

# -----------------------------------------------------------------------------
# Test: Deletion Protection
# -----------------------------------------------------------------------------
run "deletion_protection_disabled_by_default" {
  command = plan

  assert {
    condition     = aws_db_instance.this.deletion_protection == false
    error_message = "Deletion protection should be disabled by default"
  }
}

run "deletion_protection_when_enabled" {
  command = plan

  variables {
    deletion_protection = true
  }

  assert {
    condition     = aws_db_instance.this.deletion_protection == true
    error_message = "Deletion protection should be enabled when configured"
  }
}

# -----------------------------------------------------------------------------
# Test: Tags Applied
# -----------------------------------------------------------------------------
run "tags_applied" {
  command = plan

  assert {
    condition     = contains(keys(aws_db_instance.this.tags), "Project")
    error_message = "RDS instance should have custom tags applied"
  }

  assert {
    condition     = contains(keys(aws_db_instance.this.tags), "Name")
    error_message = "RDS instance should have Name tag"
  }
}
