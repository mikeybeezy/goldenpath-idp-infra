locals {
  environment_tags = var.environment != "" ? { Environment = var.environment } : {}
}

// EKS control-plane role (assumed by eks.amazonaws.com).
resource "aws_iam_role" "eks_cluster" {
  name = var.cluster_role_name

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = merge(var.tags, local.environment_tags)
}




// Attach required EKS control-plane policies.
resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  role       = aws_iam_role.eks_cluster.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}

resource "aws_iam_role_policy_attachment" "eks_vpc_resource_controller" {
  role       = aws_iam_role.eks_cluster.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSVPCResourceController"
}

// Node group role (assumed by EC2 instances).
resource "aws_iam_role" "eks_node_group" {
  name = var.node_group_role_name

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = merge(var.tags, local.environment_tags)
}


data "tls_certificate" "eks_oidc" {
  count = var.enable_oidc_role ? 1 : 0
  url   = var.oidc_issuer_url
}

data "aws_iam_policy_document" "eks_oidc_assume" {
  count = var.enable_oidc_role ? 1 : 0

  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    effect  = "Allow"

    condition {
      test     = "StringEquals"
      variable = "${replace(var.oidc_issuer_url, "https://", "")}:aud"
      values   = [var.oidc_audience]
    }

    condition {
      test     = "StringEquals"
      variable = "${replace(var.oidc_issuer_url, "https://", "")}:sub"
      values   = [var.oidc_subject]
    }

    principals {
      type        = "Federated"
      identifiers = [var.oidc_provider_arn]
    }
  }
}

resource "aws_iam_role" "eks_oidc" {
  count              = var.enable_oidc_role ? 1 : 0
  name               = var.oidc_role_name
  assume_role_policy = data.aws_iam_policy_document.eks_oidc_assume[0].json
  tags               = merge(var.tags, local.environment_tags)
}
