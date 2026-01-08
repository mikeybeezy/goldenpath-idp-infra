resource "aws_iam_role" "backstage" {
  name = var.role_name

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRoleWithWebIdentity"
        Effect = "Allow"
        Principal = {
          Federated = var.oidc_provider_arn
        }
        Condition = {
          StringEquals = {
            "${replace(var.oidc_issuer_url, "https://", "")}:sub" : "system:serviceaccount:${var.namespace}:${var.service_account_name}",
            "${replace(var.oidc_issuer_url, "https://", "")}:aud" : "sts.amazonaws.com"
          }
        }
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_policy" "backstage_ecr" {
  name        = "${var.role_name}-ecr-policy"
  description = "Permissions for Backstage to interact with ECR"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:DescribeRepositories",
          "ecr:ListImages",
          "ecr:DescribeImages"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "backstage_ecr" {
  policy_arn = aws_iam_policy.backstage_ecr.arn
  role       = aws_iam_role.backstage.name
}

# Optional: Add S3 permissions if TechDocs is stored in S3
resource "aws_iam_policy" "backstage_s3" {
  count       = var.enable_s3_techdocs ? 1 : 0
  name        = "${var.role_name}-s3-policy"
  description = "Permissions for Backstage to access TechDocs in S3"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Effect = "Allow"
        Resource = [
          "arn:aws:s3:::${var.techdocs_bucket_name}",
          "arn:aws:s3:::${var.techdocs_bucket_name}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "backstage_s3" {
  count      = var.enable_s3_techdocs ? 1 : 0
  policy_arn = aws_iam_policy.backstage_s3[0].arn
  role       = aws_iam_role.backstage.name
}
