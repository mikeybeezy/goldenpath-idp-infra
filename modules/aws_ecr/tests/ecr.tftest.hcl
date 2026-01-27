# ---
# id: TFTEST-ECR-001
# type: terraform-test
# owner: platform-team
# status: active
# maturity: 1
# ---
# Terraform native tests for aws_ecr module
# Run with: cd modules/aws_ecr && terraform init && terraform test

# -----------------------------------------------------------------------------
# Mock Provider Configuration
# -----------------------------------------------------------------------------
mock_provider "aws" {}

# -----------------------------------------------------------------------------
# Variables Block - Shared test inputs (low risk)
# -----------------------------------------------------------------------------
variables {
  name        = "test-repo"
  environment = "test"

  metadata = {
    id    = "ECR-TEST-001"
    owner = "platform-team"
    risk  = "low"
  }

  tags = {
    Project   = "goldenpath-idp"
    ManagedBy = "terraform"
  }
}

# -----------------------------------------------------------------------------
# Test: Repository Name
# -----------------------------------------------------------------------------
run "repository_name_set" {
  command = plan

  assert {
    condition     = aws_ecr_repository.this.name == var.name
    error_message = "ECR repository name should match var.name"
  }
}

# -----------------------------------------------------------------------------
# Test: Scan on Push Always Enabled
# -----------------------------------------------------------------------------
run "scan_on_push_always_enabled" {
  command = plan

  assert {
    condition     = aws_ecr_repository.this.image_scanning_configuration[0].scan_on_push == true
    error_message = "Scan on push should always be enabled regardless of risk level"
  }
}

# -----------------------------------------------------------------------------
# Test: Low Risk Policy
# -----------------------------------------------------------------------------
run "low_risk_policy" {
  command = plan

  variables {
    metadata = {
      id    = "ECR-LOW-001"
      owner = "platform-team"
      risk  = "low"
    }
  }

  assert {
    condition     = aws_ecr_repository.this.image_tag_mutability == "MUTABLE"
    error_message = "Low risk repos should have MUTABLE tags"
  }

  assert {
    condition     = aws_ecr_repository.this.encryption_configuration[0].encryption_type == "AES256"
    error_message = "Low risk repos should use AES256 encryption"
  }
}

# -----------------------------------------------------------------------------
# Test: Medium Risk Policy
# -----------------------------------------------------------------------------
run "medium_risk_policy" {
  command = plan

  variables {
    metadata = {
      id    = "ECR-MED-001"
      owner = "platform-team"
      risk  = "medium"
    }
  }

  assert {
    condition     = aws_ecr_repository.this.image_tag_mutability == "MUTABLE"
    error_message = "Medium risk repos should have MUTABLE tags"
  }

  assert {
    condition     = aws_ecr_repository.this.encryption_configuration[0].encryption_type == "AES256"
    error_message = "Medium risk repos should use AES256 encryption"
  }
}

# -----------------------------------------------------------------------------
# Test: High Risk Policy
# -----------------------------------------------------------------------------
run "high_risk_policy" {
  command = plan

  variables {
    metadata = {
      id    = "ECR-HIGH-001"
      owner = "platform-team"
      risk  = "high"
    }
  }

  assert {
    condition     = aws_ecr_repository.this.image_tag_mutability == "IMMUTABLE"
    error_message = "High risk repos should have IMMUTABLE tags"
  }

  assert {
    condition     = aws_ecr_repository.this.encryption_configuration[0].encryption_type == "KMS"
    error_message = "High risk repos should use KMS encryption"
  }
}

# -----------------------------------------------------------------------------
# Test: Governance Metadata Tags
# -----------------------------------------------------------------------------
run "governance_metadata_tags" {
  command = plan

  assert {
    condition     = lookup(aws_ecr_repository.this.tags, "goldenpath.idp/id", "") == var.metadata.id
    error_message = "Repository should have governance ID tag"
  }

  assert {
    condition     = lookup(aws_ecr_repository.this.tags, "goldenpath.idp/owner", "") == var.metadata.owner
    error_message = "Repository should have governance owner tag"
  }

  assert {
    condition     = lookup(aws_ecr_repository.this.tags, "goldenpath.idp/risk", "") == var.metadata.risk
    error_message = "Repository should have governance risk tag"
  }
}

# -----------------------------------------------------------------------------
# Test: Environment Tag
# -----------------------------------------------------------------------------
run "environment_tag_applied" {
  command = plan

  assert {
    condition     = lookup(aws_ecr_repository.this.tags, "Environment", "") == var.environment
    error_message = "Repository should have Environment tag when environment is set"
  }
}

# -----------------------------------------------------------------------------
# Test: Custom Tags Merged
# -----------------------------------------------------------------------------
run "custom_tags_merged" {
  command = plan

  assert {
    condition     = lookup(aws_ecr_repository.this.tags, "Project", "") == "goldenpath-idp"
    error_message = "Repository should have custom Project tag"
  }

  assert {
    condition     = lookup(aws_ecr_repository.this.tags, "ManagedBy", "") == "terraform"
    error_message = "Repository should have custom ManagedBy tag"
  }
}

# -----------------------------------------------------------------------------
# Test: Lifecycle Policy Created
# -----------------------------------------------------------------------------
run "lifecycle_policy_created" {
  command = plan

  assert {
    condition     = aws_ecr_lifecycle_policy.this.repository == var.name
    error_message = "Lifecycle policy should be attached to the repository"
  }
}

# -----------------------------------------------------------------------------
# Test: Force Delete Default
# -----------------------------------------------------------------------------
run "force_delete_disabled_by_default" {
  command = plan

  assert {
    condition     = aws_ecr_repository.this.force_delete == false
    error_message = "Force delete should be disabled by default"
  }
}

run "force_delete_when_enabled" {
  command = plan

  variables {
    force_delete = true
  }

  assert {
    condition     = aws_ecr_repository.this.force_delete == true
    error_message = "Force delete should be enabled when configured"
  }
}
