# modules/aws_ecr/locals.tf
locals {
  risk_policies = {
    low = {
      tag_mutability  = "MUTABLE"
      encryption_type = "AES256"
      keep_count      = 20
    }
    medium = {
      tag_mutability  = "MUTABLE"
      encryption_type = "AES256"
      keep_count      = 30
    }
    high = {
      tag_mutability  = "IMMUTABLE"
      encryption_type = "KMS"
      keep_count      = 50
    }
  }

  policy = local.risk_policies[var.metadata.risk]
}
