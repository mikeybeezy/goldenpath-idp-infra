resource "aws_ecr_repository" "this" {
  name                 = var.name
  image_tag_mutability = local.policy.tag_mutability
  force_delete         = var.force_delete

  image_scanning_configuration {
    scan_on_push = true # Always enabled for all risk levels
  }

  encryption_configuration {
    encryption_type = local.policy.encryption_type
    kms_key         = local.policy.encryption_type == "KMS" ? var.kms_key : null
  }

  tags = merge(
    var.tags,
    var.environment != "" ? { Environment = var.environment } : {},
    var.metadata != null ? {
      "goldenpath.idp/id"    = var.metadata.id
      "goldenpath.idp/owner" = var.metadata.owner
      "goldenpath.idp/risk"  = var.metadata.risk
    } : {}
  )

  lifecycle {
    precondition {
      condition     = var.metadata != null
      error_message = "Metadata is REQUIRED for all ECR repositories. This resource cannot be created without governance metadata."
    }

    precondition {
      condition     = var.metadata != null && length(var.metadata.id) > 0
      error_message = "Metadata ID cannot be empty. All repositories must have a valid governance ID."
    }

    precondition {
      condition     = var.metadata != null && length(var.metadata.owner) > 0
      error_message = "Metadata owner cannot be empty. All repositories must have a designated owner team."
    }

    precondition {
      condition     = var.metadata != null && contains(["low", "medium", "high"], var.metadata.risk)
      error_message = "Metadata risk must be one of: low, medium, high"
    }
  }
}

resource "aws_ecr_lifecycle_policy" "this" {
  repository = aws_ecr_repository.this.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last ${local.policy.keep_count} images (${var.metadata.risk} risk policy)"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = local.policy.keep_count
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}
