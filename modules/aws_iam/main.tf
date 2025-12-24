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

data "aws_iam_policy_document" "cluster_autoscaler_assume" {
  count = var.enable_autoscaler_role ? 1 : 0

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
      values   = ["system:serviceaccount:${var.autoscaler_service_account_namespace}:${var.autoscaler_service_account_name}"]
    }

    principals {
      type        = "Federated"
      identifiers = [var.oidc_provider_arn]
    }
  }
}

resource "aws_iam_role" "cluster_autoscaler" {
  count              = var.enable_autoscaler_role ? 1 : 0
  name               = var.autoscaler_role_name
  assume_role_policy = data.aws_iam_policy_document.cluster_autoscaler_assume[0].json
  tags               = merge(var.tags, local.environment_tags)
}

data "aws_iam_policy_document" "cluster_autoscaler" {
  count = var.enable_autoscaler_role ? 1 : 0

  statement {
    effect = "Allow"
    actions = [
      "autoscaling:DescribeAutoScalingGroups",
      "autoscaling:DescribeAutoScalingInstances",
      "autoscaling:DescribeLaunchConfigurations",
      "autoscaling:DescribeScalingActivities",
      "autoscaling:DescribeTags",
      "autoscaling:SetDesiredCapacity",
      "autoscaling:TerminateInstanceInAutoScalingGroup",
      "autoscaling:UpdateAutoScalingGroup",
      "ec2:DescribeLaunchTemplateVersions",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "cluster_autoscaler" {
  count       = var.enable_autoscaler_role ? 1 : 0
  name        = "${var.autoscaler_role_name}-policy"
  description = "IAM policy for Kubernetes Cluster Autoscaler."
  policy      = data.aws_iam_policy_document.cluster_autoscaler[0].json
  tags        = merge(var.tags, local.environment_tags)
}

resource "aws_iam_role_policy_attachment" "cluster_autoscaler" {
  count      = var.enable_autoscaler_role ? 1 : 0
  role       = aws_iam_role.cluster_autoscaler[0].name
  policy_arn = aws_iam_policy.cluster_autoscaler[0].arn
}

data "aws_iam_policy_document" "lb_controller_assume" {
  count = var.enable_lb_controller_role ? 1 : 0

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
      values   = ["system:serviceaccount:${var.lb_controller_service_account_namespace}:${var.lb_controller_service_account_name}"]
    }

    principals {
      type        = "Federated"
      identifiers = [var.oidc_provider_arn]
    }
  }
}

resource "aws_iam_role" "lb_controller" {
  count              = var.enable_lb_controller_role ? 1 : 0
  name               = var.lb_controller_role_name
  assume_role_policy = data.aws_iam_policy_document.lb_controller_assume[0].json
  tags               = merge(var.tags, local.environment_tags)
}

data "aws_iam_policy_document" "lb_controller" {
  count = var.enable_lb_controller_role ? 1 : 0

  statement {
    effect = "Allow"
    actions = [
      "iam:CreateServiceLinkedRole",
      "ec2:DescribeAccountAttributes",
      "ec2:DescribeAddresses",
      "ec2:DescribeAvailabilityZones",
      "ec2:DescribeInternetGateways",
      "ec2:DescribeRouteTables",
      "ec2:DescribeVpcs",
      "ec2:DescribeVpcPeeringConnections",
      "ec2:DescribeSubnets",
      "ec2:DescribeSecurityGroups",
      "ec2:DescribeInstances",
      "ec2:DescribeNetworkInterfaces",
      "ec2:DescribeTags",
      "ec2:GetCoipPoolUsage",
      "ec2:DescribeCoipPools",
      "elasticloadbalancing:DescribeLoadBalancers",
      "elasticloadbalancing:DescribeLoadBalancerAttributes",
      "elasticloadbalancing:DescribeListeners",
      "elasticloadbalancing:DescribeListenerCertificates",
      "elasticloadbalancing:DescribeSSLPolicies",
      "elasticloadbalancing:DescribeRules",
      "elasticloadbalancing:DescribeTargetGroups",
      "elasticloadbalancing:DescribeTargetGroupAttributes",
      "elasticloadbalancing:DescribeTargetHealth",
      "elasticloadbalancing:DescribeTags",
      "elasticloadbalancing:DescribeTrustStores",
      "elasticloadbalancing:DescribeTrustStoreAssociations",
      "elasticloadbalancing:DescribeCapacityReservation",
      "elasticloadbalancing:DescribeListenerAttributes",
    ]
    resources = ["*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "ec2:AuthorizeSecurityGroupIngress",
      "ec2:RevokeSecurityGroupIngress",
      "ec2:CreateSecurityGroup",
      "ec2:DeleteSecurityGroup",
    ]
    resources = ["*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "ec2:CreateTags",
      "ec2:DeleteTags",
    ]
    resources = [
      "arn:aws:ec2:*:*:security-group/*",
    ]
    condition {
      test     = "StringEquals"
      variable = "ec2:CreateAction"
      values   = ["CreateSecurityGroup"]
    }
  }

  statement {
    effect = "Allow"
    actions = [
      "ec2:CreateTags",
      "ec2:DeleteTags",
    ]
    resources = [
      "arn:aws:ec2:*:*:security-group/*",
      "arn:aws:elasticloadbalancing:*:*:loadbalancer/app/*/*",
      "arn:aws:elasticloadbalancing:*:*:loadbalancer/net/*/*",
      "arn:aws:elasticloadbalancing:*:*:targetgroup/*/*",
      "arn:aws:elasticloadbalancing:*:*:listener/app/*/*/*",
      "arn:aws:elasticloadbalancing:*:*:listener/net/*/*/*",
      "arn:aws:elasticloadbalancing:*:*:listener-rule/app/*/*/*",
      "arn:aws:elasticloadbalancing:*:*:listener-rule/net/*/*/*",
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "elasticloadbalancing:CreateLoadBalancer",
      "elasticloadbalancing:CreateTargetGroup",
      "elasticloadbalancing:CreateListener",
      "elasticloadbalancing:DeleteListener",
      "elasticloadbalancing:CreateRule",
      "elasticloadbalancing:DeleteRule",
      "elasticloadbalancing:ModifyLoadBalancerAttributes",
      "elasticloadbalancing:ModifyTargetGroup",
      "elasticloadbalancing:ModifyTargetGroupAttributes",
      "elasticloadbalancing:ModifyListener",
      "elasticloadbalancing:AddTags",
      "elasticloadbalancing:RemoveTags",
      "elasticloadbalancing:DeleteLoadBalancer",
      "elasticloadbalancing:DeleteTargetGroup",
      "elasticloadbalancing:ModifyRule",
      "elasticloadbalancing:SetWebAcl",
      "elasticloadbalancing:ModifyListenerAttributes",
      "elasticloadbalancing:ModifyCapacityReservation",
      "elasticloadbalancing:ModifyTargetGroupAttributes",
      "elasticloadbalancing:ModifyLoadBalancerAttributes",
    ]
    resources = ["*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "iam:CreateServiceLinkedRole",
      "cognito-idp:DescribeUserPoolClient",
      "acm:ListCertificates",
      "acm:DescribeCertificate",
      "iam:ListServerCertificates",
      "iam:GetServerCertificate",
      "waf-regional:GetWebACL",
      "waf-regional:GetWebACLForResource",
      "waf-regional:AssociateWebACL",
      "waf-regional:DisassociateWebACL",
      "wafv2:GetWebACL",
      "wafv2:GetWebACLForResource",
      "wafv2:AssociateWebACL",
      "wafv2:DisassociateWebACL",
      "shield:GetSubscriptionState",
      "shield:DescribeProtection",
      "shield:CreateProtection",
      "shield:DeleteProtection",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "lb_controller" {
  count       = var.enable_lb_controller_role ? 1 : 0
  name        = "${var.lb_controller_role_name}-policy"
  description = "IAM policy for AWS Load Balancer Controller."
  policy      = data.aws_iam_policy_document.lb_controller[0].json
  tags        = merge(var.tags, local.environment_tags)
}

resource "aws_iam_role_policy_attachment" "lb_controller" {
  count      = var.enable_lb_controller_role ? 1 : 0
  role       = aws_iam_role.lb_controller[0].name
  policy_arn = aws_iam_policy.lb_controller[0].arn
}
