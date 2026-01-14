environment       = "dev"
aws_region        = "eu-west-2"
vpc_cidr          = "10.0.0.0/16"
owner_team        = "platform-team"
cluster_lifecycle = "ephemeral"
# NEED TO UPDATE persistent or ephemeral
build_id = "13-01-26-90"


public_subnets = [
  {
    name              = "goldenpath-dev-public-a"
    cidr_block        = "10.0.1.0/24"
    availability_zone = "eu-west-2a"
  },
  {
    name              = "goldenpath-dev-public-b"
    cidr_block        = "10.0.2.0/24"
    availability_zone = "eu-west-2b"
  }
]

private_subnets = [
  {
    name              = "goldenpath-dev-private-a"
    cidr_block        = "10.0.11.0/24"
    availability_zone = "eu-west-2a"
  },
  {
    name              = "goldenpath-dev-private-b"
    cidr_block        = "10.0.12.0/24"
    availability_zone = "eu-west-2b"
  }
]

common_tags = {
  Project = "goldenpath-idp"
  Owner   = "platform-team"
}

# Base EC2 compute (disabled by default; set enabled = true to provision)
compute_config = {
  enabled                       = true
  name                          = "goldenpath-dev-app"
  ami_id                        = "ami-0a0ff88d0f3f85a14"
  instance_type                 = "t3.micro"
  subnet_type                   = "private"
  additional_security_group_ids = []
  ssh_key_name                  = null
  user_data                     = null
  iam_instance_profile          = null
  network_interface_description = "Golden Path dev instance"
  root_volume_size              = 20
  root_volume_type              = "gp3"
  root_volume_encrypted         = true
}

iam_config = {
  enabled                                 = true
  cluster_role_name                       = ""
  node_group_role_name                    = ""
  oidc_role_name                          = ""
  oidc_issuer_url                         = ""
  oidc_provider_arn                       = ""
  oidc_audience                           = "sts.amazonaws.com"
  oidc_subject                            = ""
  enable_autoscaler_role                  = true
  autoscaler_role_name                    = "goldenpath-idp-cluster-autoscaler"
  autoscaler_policy_arn                   = "arn:aws:iam::593517239005:policy/golden-path-cluster-autoscaler-policy"
  autoscaler_service_account_namespace    = "kube-system"
  autoscaler_service_account_name         = "cluster-autoscaler"
  enable_lb_controller_role               = true
  lb_controller_role_name                 = "goldenpath-idp-aws-load-balancer-controller"
  lb_controller_policy_arn                = "arn:aws:iam::593517239005:policy/goldenpath-load-balancer-controller-policy"
  lb_controller_service_account_namespace = "kube-system"
  lb_controller_service_account_name      = "aws-load-balancer-controller"
}


addon_replica_counts = {
  aws-ebs-csi-driver  = 1
  aws-efs-csi-driver  = 1
  snapshot-controller = 1
}

enable_storage_addons = true
enable_k8s_resources  = true

eks_config = {
  enabled                       = true
  cluster_name                  = "goldenpath-dev-eks"
  version                       = "1.29"
  enable_ssh_break_glass        = false
  ssh_key_name                  = null
  ssh_source_security_group_ids = []
  node_group = {
    name           = "dev-default"
    min_size       = 6
    max_size       = 8
    desired_size   = 6
    instance_types = ["t3.small"]
    disk_size      = 20
    capacity_type  = "ON_DEMAND"
    update_config = {
      max_unavailable = 1
    }
  }
}

# SSH break-glass (pass ssh_key_name via CLI or TF_VAR_ssh_key_name)
enable_ssh_break_glass        = false
ssh_key_name                  = null
ssh_source_security_group_ids = []

# Bootstrap mode keeps node sizing stable during bring-up.
bootstrap_mode = true
bootstrap_node_group = {
  min_size     = 6
  desired_size = 6
  max_size     = 8
}

# Registry Catalog
# NOTE: ECR repositories are account-scoped and persist across ephemeral builds.
# They should be managed separately, not recreated per cluster.
# Uncomment only for initial account setup or when adding new repositories.
ecr_repositories = {
  # "test-app-dev" = {
  #   metadata = {
  #     id    = "REGISTRY_TEST_APP_DEV"
  #     owner = "app-team-test"
  #     risk  = "low"
  #   }
  # }

  # "new-wp-reg-2" = {
  #   metadata = {
  #     id    = "REGISTRY_NEW_WP_REG_2"
  #     owner = "michael-babs-2"
  #     risk  = "low"
  #   }
  # }

  # "new-app-16" = {
  #   metadata = {
  #     id    = "REGISTRY_NEW_APP_16"
  #     owner = "michael-babs-16"
  #     risk  = "low"
  #   }
  # }

  # "new-app-15" = {
  #   metadata = {
  #     id    = "REGISTRY_NEW_APP_15"
  #     owner = "michael-babs-15"
  #     risk  = "low"
  #   }
  # }

  # "new-app-14" = {
  #   metadata = {
  #     id    = "REGISTRY_NEW_APP_14"
  #     owner = "michael-babs-14"
  #     risk  = "low"
  #   }
  # }

  # "new-app-13" = {
  #   metadata = {
  #     id    = "REGISTRY_NEW_APP_13"
  #     owner = "michael-babs-13"
  #     risk  = "low"
  #   }
  # }

  # "new-app-10" = {
  #   metadata = {
  #     id    = "REGISTRY_NEW_APP_10"
  #     owner = "michael-babs-10"
  #     risk  = "low"
  #   }
  # }

  # "my-reg-app-3" = {
  #   metadata = {
  #     id    = "REGISTRY_MY_REG_APP_3"
  #     owner = "michael-babs-3"
  #     risk  = "low"
  #   }
  # }

  # "new-wp-reg2" = {
  #   metadata = {
  #     id    = "REGISTRY_NEW_WP_REG2"
  #     owner = "platform-team"
  #     risk  = "low"
  #   }
  # }
}

# Secret Catalog
# NOTE: Secrets Manager is a platform service managed through Backstage SecretRequest workflow.
# Secrets are environment-scoped, NOT cluster-scoped. They persist independently of EKS clusters.
# DO NOT manage secrets through EKS terraform - use the SecretRequest workflow instead.
# See: docs/adrs/ADR-0143-secret-request-contract.md
app_secrets = {
  # "goldenpath-idp-secret-store" = {
  #   description = "Managed secret for payments in dev"
  #   metadata = {
  #     id    = "SEC-0007"
  #     owner = "app-team"
  #     risk  = "medium"
  #   }
  #   # Security policy principals
  #   read_principals        = ["arn:aws:iam::593517239005:role/goldenpath-idp-eso-role"]
  #   write_principals       = ["arn:aws:iam::593517239005:role/github-actions-secrets-writer"]
  #   break_glass_principals = ["arn:aws:iam::593517239005:role/platform-admin"]
  # }
}
