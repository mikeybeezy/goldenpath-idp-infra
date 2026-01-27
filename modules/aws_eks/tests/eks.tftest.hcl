# ---
# id: TFTEST-EKS-001
# type: terraform-test
# owner: platform-team
# status: active
# maturity: 1
# ---
# Terraform native tests for aws_eks module
# Run with: terraform test -chdir=modules/aws_eks
#
# These tests validate the module's behavior without making real AWS API calls.
# They use plan-mode assertions to verify resource configurations.

# -----------------------------------------------------------------------------
# Mock Provider Configuration
# Uses the built-in mock provider to avoid real AWS calls
# -----------------------------------------------------------------------------
mock_provider "aws" {}
mock_provider "tls" {}

# -----------------------------------------------------------------------------
# Variables Block - Shared test inputs
# -----------------------------------------------------------------------------
variables {
  cluster_name       = "test-cluster"
  kubernetes_version = "1.31"
  vpc_id             = "vpc-12345678"
  subnet_ids         = ["subnet-aaaaaaaa", "subnet-bbbbbbbb"]
  environment        = "test"

  node_group_config = {
    name           = "test-nodes"
    min_size       = 1
    max_size       = 3
    desired_size   = 2
    instance_types = ["t3.medium"]
    disk_size      = 50
    capacity_type  = "ON_DEMAND"
  }

  tags = {
    Project   = "goldenpath-idp"
    ManagedBy = "terraform"
  }

  enable_storage_addons = true
}

# -----------------------------------------------------------------------------
# Test: Cluster Creation with Correct Name
# Validates that the EKS cluster resource uses the provided cluster_name
# -----------------------------------------------------------------------------
run "cluster_name_is_set_correctly" {
  command = plan

  assert {
    condition     = aws_eks_cluster.this.name == var.cluster_name
    error_message = "EKS cluster name should match var.cluster_name"
  }

  assert {
    condition     = aws_eks_cluster.this.version == var.kubernetes_version
    error_message = "EKS cluster version should match var.kubernetes_version"
  }
}

# -----------------------------------------------------------------------------
# Test: IAM Role Naming Convention
# Validates IAM roles follow the naming convention: {cluster_name}-{role_type}
# -----------------------------------------------------------------------------
run "iam_roles_follow_naming_convention" {
  command = plan

  assert {
    condition     = aws_iam_role.cluster.name == "${var.cluster_name}-cluster-role"
    error_message = "Cluster IAM role should be named '{cluster_name}-cluster-role'"
  }

  assert {
    condition     = aws_iam_role.node_group.name == "${var.cluster_name}-node-role"
    error_message = "Node group IAM role should be named '{cluster_name}-node-role'"
  }
}

# -----------------------------------------------------------------------------
# Test: Security Group Configuration
# Validates the cluster security group is created in the correct VPC
# -----------------------------------------------------------------------------
run "security_group_in_correct_vpc" {
  command = plan

  assert {
    condition     = aws_security_group.cluster.vpc_id == var.vpc_id
    error_message = "Cluster security group should be in the specified VPC"
  }

  assert {
    condition     = aws_security_group.cluster.name == "${var.cluster_name}-cluster-sg"
    error_message = "Security group should be named '{cluster_name}-cluster-sg'"
  }
}

# -----------------------------------------------------------------------------
# Test: Node Group Scaling Configuration
# Validates the node group scaling config respects the input variables
# -----------------------------------------------------------------------------
run "node_group_scaling_configuration" {
  command = plan

  assert {
    condition     = aws_eks_node_group.this.scaling_config[0].min_size == var.node_group_config.min_size
    error_message = "Node group min_size should match configuration"
  }

  assert {
    condition     = aws_eks_node_group.this.scaling_config[0].max_size == var.node_group_config.max_size
    error_message = "Node group max_size should match configuration"
  }

  assert {
    condition     = aws_eks_node_group.this.scaling_config[0].desired_size == var.node_group_config.desired_size
    error_message = "Node group desired_size should match configuration"
  }
}

# -----------------------------------------------------------------------------
# Test: Node Group Instance Configuration
# Validates the node group uses correct instance types and disk size
# -----------------------------------------------------------------------------
run "node_group_instance_configuration" {
  command = plan

  assert {
    condition     = aws_eks_node_group.this.capacity_type == var.node_group_config.capacity_type
    error_message = "Node group capacity_type should match configuration"
  }

  assert {
    condition     = aws_eks_node_group.this.disk_size == var.node_group_config.disk_size
    error_message = "Node group disk_size should match configuration"
  }

  assert {
    condition     = tolist(aws_eks_node_group.this.instance_types) == var.node_group_config.instance_types
    error_message = "Node group instance_types should match configuration"
  }
}

# -----------------------------------------------------------------------------
# Test: Environment Tags Applied
# Validates that environment tags are merged into resources
# -----------------------------------------------------------------------------
run "environment_tags_applied" {
  command = plan

  assert {
    condition     = contains(keys(aws_eks_cluster.this.tags), "Environment")
    error_message = "EKS cluster should have Environment tag when environment is set"
  }

  assert {
    condition     = contains(keys(aws_eks_cluster.this.tags), "Project")
    error_message = "EKS cluster should include custom tags"
  }
}

# -----------------------------------------------------------------------------
# Test: Cluster Autoscaler Tags
# Validates that node group has required cluster autoscaler tags
# -----------------------------------------------------------------------------
run "cluster_autoscaler_tags" {
  command = plan

  assert {
    condition     = lookup(aws_eks_node_group.this.tags, "k8s.io/cluster-autoscaler/enabled", "") == "true"
    error_message = "Node group should have cluster-autoscaler enabled tag"
  }

  assert {
    condition     = lookup(aws_eks_node_group.this.tags, "k8s.io/cluster-autoscaler/${var.cluster_name}", "") == "owned"
    error_message = "Node group should have cluster-autoscaler ownership tag"
  }
}

# -----------------------------------------------------------------------------
# Test: Storage Addons Enabled
# Validates storage addons are created when enable_storage_addons is true
# -----------------------------------------------------------------------------
run "storage_addons_enabled" {
  command = plan

  assert {
    condition     = length(aws_eks_addon.ebs_csi_driver) == 1
    error_message = "EBS CSI driver addon should be created when storage addons enabled"
  }

  assert {
    condition     = length(aws_eks_addon.efs_csi_driver) == 1
    error_message = "EFS CSI driver addon should be created when storage addons enabled"
  }

  assert {
    condition     = length(aws_eks_addon.snapshot_controller) == 1
    error_message = "Snapshot controller addon should be created when storage addons enabled"
  }
}

# -----------------------------------------------------------------------------
# Test: Storage Addons Disabled
# Validates storage addons are NOT created when enable_storage_addons is false
# -----------------------------------------------------------------------------
run "storage_addons_disabled" {
  command = plan

  variables {
    enable_storage_addons = false
  }

  assert {
    condition     = length(aws_eks_addon.ebs_csi_driver) == 0
    error_message = "EBS CSI driver addon should NOT be created when storage addons disabled"
  }

  assert {
    condition     = length(aws_eks_addon.efs_csi_driver) == 0
    error_message = "EFS CSI driver addon should NOT be created when storage addons disabled"
  }

  assert {
    condition     = length(aws_eks_addon.snapshot_controller) == 0
    error_message = "Snapshot controller addon should NOT be created when storage addons disabled"
  }
}

# -----------------------------------------------------------------------------
# Test: Core Addons Always Present
# Validates that coredns, kube-proxy, and vpc-cni are always created
# -----------------------------------------------------------------------------
run "core_addons_always_present" {
  command = plan

  assert {
    condition     = aws_eks_addon.coredns.addon_name == "coredns"
    error_message = "CoreDNS addon should always be created"
  }

  assert {
    condition     = aws_eks_addon.kube_proxy.addon_name == "kube-proxy"
    error_message = "kube-proxy addon should always be created"
  }

  assert {
    condition     = aws_eks_addon.vpc_cni.addon_name == "vpc-cni"
    error_message = "vpc-cni addon should always be created"
  }
}

# -----------------------------------------------------------------------------
# Test: SSH Break-Glass Disabled by Default
# Validates that remote SSH access is not configured by default
# -----------------------------------------------------------------------------
run "ssh_break_glass_disabled_by_default" {
  command = plan

  variables {
    enable_ssh_break_glass = false
  }

  assert {
    condition     = length(aws_eks_node_group.this.remote_access) == 0
    error_message = "Node group should not have remote_access when SSH break-glass is disabled"
  }
}

# -----------------------------------------------------------------------------
# Test: Access Config Defaults
# Validates the default EKS access configuration
# -----------------------------------------------------------------------------
run "access_config_defaults" {
  command = plan

  assert {
    condition     = aws_eks_cluster.this.access_config[0].authentication_mode == "API_AND_CONFIG_MAP"
    error_message = "Default authentication mode should be API_AND_CONFIG_MAP"
  }

  assert {
    condition     = aws_eks_cluster.this.access_config[0].bootstrap_cluster_creator_admin_permissions == true
    error_message = "Bootstrap cluster creator admin permissions should be true by default"
  }
}

# -----------------------------------------------------------------------------
# Test: Minimum Scaling Validation
# Validates that desired_size is within min/max bounds
# -----------------------------------------------------------------------------
run "scaling_bounds_validation" {
  command = plan

  variables {
    node_group_config = {
      name           = "bounded-nodes"
      min_size       = 2
      max_size       = 10
      desired_size   = 5
      instance_types = ["t3.large"]
      disk_size      = 100
      capacity_type  = "SPOT"
    }
  }

  assert {
    condition     = aws_eks_node_group.this.scaling_config[0].desired_size >= aws_eks_node_group.this.scaling_config[0].min_size
    error_message = "desired_size must be >= min_size"
  }

  assert {
    condition     = aws_eks_node_group.this.scaling_config[0].desired_size <= aws_eks_node_group.this.scaling_config[0].max_size
    error_message = "desired_size must be <= max_size"
  }
}
