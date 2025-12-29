locals {
  node_group             = var.node_group_config
  environment_tags       = var.environment != "" ? { Environment = var.environment } : {}
  addon_replica_counts   = var.addon_replica_counts
  ebs_replica_count      = lookup(var.addon_replica_counts, "aws-ebs-csi-driver", null)
  efs_replica_count      = lookup(var.addon_replica_counts, "aws-efs-csi-driver", null)
  snapshot_replica_count = lookup(var.addon_replica_counts, "snapshot-controller", null)
}

resource "aws_iam_role" "cluster" {
  name = "${var.cluster_name}-cluster-role"

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

  tags = merge(
    {
      Name = "${var.cluster_name}-cluster-role"
    },
    var.tags,
    local.environment_tags,
  )
}

resource "aws_iam_role_policy_attachment" "cluster" {
  for_each = toset([
    "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy",
    "arn:aws:iam::aws:policy/AmazonEKSVPCResourceController",
  ])

  policy_arn = each.value
  role       = aws_iam_role.cluster.name
}

resource "aws_security_group" "cluster" {
  name        = "${var.cluster_name}-cluster-sg"
  description = "Security group for EKS cluster control plane"
  vpc_id      = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.cluster_name}-cluster-sg"
    },
    local.environment_tags,
  )
}

resource "aws_eks_cluster" "this" {
  name     = var.cluster_name
  version  = var.kubernetes_version
  role_arn = aws_iam_role.cluster.arn

  access_config {
    authentication_mode                         = var.access_config.authentication_mode
    bootstrap_cluster_creator_admin_permissions = var.access_config.bootstrap_cluster_creator_admin_permissions
  }

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = [aws_security_group.cluster.id]
  }

  tags = merge(var.tags, local.environment_tags)

  depends_on = [aws_iam_role_policy_attachment.cluster]
}

data "tls_certificate" "oidc" {
  url = aws_eks_cluster.this.identity[0].oidc[0].issuer
}

resource "aws_iam_openid_connect_provider" "this" {
  url = aws_eks_cluster.this.identity[0].oidc[0].issuer

  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.oidc.certificates[0].sha1_fingerprint]

  tags = merge(
    var.tags,
    local.environment_tags,
    {
      Name = "${var.cluster_name}-oidc-provider"
    },
  )
}

resource "aws_iam_role" "node_group" {
  name = "${var.cluster_name}-node-role"

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

  tags = merge(
    var.tags,
    {
      Name = "${var.cluster_name}-node-role"
    },
    local.environment_tags,
  )
}

resource "aws_iam_role_policy_attachment" "node_group" {
  for_each = toset([
    "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy",
    "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy",
    "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly",
    "arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy",
  ])

  policy_arn = each.value
  role       = aws_iam_role.node_group.name
}

resource "aws_eks_node_group" "this" {
  cluster_name    = aws_eks_cluster.this.name
  node_group_name = local.node_group.name
  node_role_arn   = aws_iam_role.node_group.arn
  subnet_ids      = var.subnet_ids
  capacity_type   = local.node_group.capacity_type
  disk_size       = local.node_group.disk_size
  instance_types  = local.node_group.instance_types

  dynamic "remote_access" {
    for_each = var.enable_ssh_break_glass ? [1] : []

    content {
      ec2_ssh_key               = var.ssh_key_name
      source_security_group_ids = var.ssh_source_security_group_ids
    }
  }

  dynamic "update_config" {
    for_each = [local.node_group.update_config == null ? { max_unavailable = 1 } : local.node_group.update_config]

    content {
      max_unavailable            = try(update_config.value.max_unavailable, null)
      max_unavailable_percentage = try(update_config.value.max_unavailable_percentage, null)
    }
  }

  scaling_config {
    desired_size = local.node_group.desired_size
    max_size     = local.node_group.max_size
    min_size     = local.node_group.min_size
  }

  tags = merge(var.tags, local.environment_tags)

  depends_on = [aws_iam_role_policy_attachment.node_group]
}

resource "aws_eks_addon" "ebs_csi_driver" {
  count         = var.enable_storage_addons ? 1 : 0
  cluster_name  = aws_eks_cluster.this.name
  addon_name    = "aws-ebs-csi-driver"
  addon_version = lookup(var.addon_versions, "aws-ebs-csi-driver", null)
  configuration_values = local.ebs_replica_count != null ? jsonencode({
    controller = {
      replicaCount = local.ebs_replica_count
    }
  }) : null
  resolve_conflicts_on_create = "OVERWRITE"
  resolve_conflicts_on_update = "OVERWRITE"

  tags = merge(
    var.tags,
    local.environment_tags,
    {
      Name = "${var.cluster_name}-aws-ebs-csi-driver"
    },
  )

  depends_on = [aws_eks_node_group.this]
}

resource "aws_eks_addon" "efs_csi_driver" {
  count         = var.enable_storage_addons ? 1 : 0
  cluster_name  = aws_eks_cluster.this.name
  addon_name    = "aws-efs-csi-driver"
  addon_version = lookup(var.addon_versions, "aws-efs-csi-driver", null)
  configuration_values = local.efs_replica_count != null ? jsonencode({
    controller = {
      replicaCount = local.efs_replica_count
    }
  }) : null
  resolve_conflicts_on_create = "OVERWRITE"
  resolve_conflicts_on_update = "OVERWRITE"

  tags = merge(
    var.tags,
    local.environment_tags,
    {
      Name = "${var.cluster_name}-aws-efs-csi-driver"
    },
  )

  depends_on = [aws_eks_node_group.this]
}

resource "aws_eks_addon" "snapshot_controller" {
  count                       = var.enable_storage_addons ? 1 : 0
  cluster_name                = aws_eks_cluster.this.name
  addon_name                  = "snapshot-controller"
  addon_version               = lookup(var.addon_versions, "snapshot-controller", null)
  resolve_conflicts_on_create = "OVERWRITE"
  resolve_conflicts_on_update = "OVERWRITE"

  tags = merge(
    var.tags,
    local.environment_tags,
    {
      Name = "${var.cluster_name}-snapshot-controller"
    },
  )

  depends_on = [aws_eks_node_group.this]
}

resource "aws_eks_addon" "coredns" {
  cluster_name                = aws_eks_cluster.this.name
  addon_name                  = "coredns"
  addon_version               = lookup(var.addon_versions, "coredns", null)
  resolve_conflicts_on_create = "OVERWRITE"
  resolve_conflicts_on_update = "OVERWRITE"

  tags = merge(
    var.tags,
    local.environment_tags,
    {
      Name = "${var.cluster_name}-coredns"
    },
  )

  depends_on = [aws_eks_cluster.this]
}

resource "aws_eks_addon" "kube_proxy" {
  cluster_name                = aws_eks_cluster.this.name
  addon_name                  = "kube-proxy"
  addon_version               = lookup(var.addon_versions, "kube-proxy", null)
  resolve_conflicts_on_create = "OVERWRITE"
  resolve_conflicts_on_update = "OVERWRITE"

  tags = merge(
    var.tags,
    local.environment_tags,
    {
      Name = "${var.cluster_name}-kube-proxy"
    },
  )

  depends_on = [aws_eks_cluster.this]
}

resource "aws_eks_addon" "vpc_cni" {
  cluster_name                = aws_eks_cluster.this.name
  addon_name                  = "vpc-cni"
  addon_version               = lookup(var.addon_versions, "vpc-cni", null)
  resolve_conflicts_on_create = "OVERWRITE"
  resolve_conflicts_on_update = "OVERWRITE"

  tags = merge(
    var.tags,
    local.environment_tags,
    {
      Name = "${var.cluster_name}-vpc-cni"
    },
  )

  depends_on = [aws_eks_cluster.this]
}
