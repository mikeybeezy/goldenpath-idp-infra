environment       = "dev"
aws_region        = "eu-west-2"
vpc_cidr          = "10.0.0.0/16"
owner_team        = "platform-team"
cluster_lifecycle = "ephemeral"
# NEED TO UPDATE persistent or ephemeral
build_id = "15-01-26-15"

# -----------------------------------------------------------------------------
# CRITICAL CONFIGURATION (Moved to Top)
# -----------------------------------------------------------------------------

# Secret Catalog
# These secrets are created (empty) by Terraform. You must populate values in AWS Console.
app_secrets = {
  "goldenpath/dev/keycloak/admin" = {
    description = "Keycloak initial admin credentials"
    metadata = {
      id    = "SEC-KEYCLOAK-ADMIN"
      owner = "platform-team"
      risk  = "low"
    }
    read_principals        = []
    write_principals       = []
    break_glass_principals = []
  }

  "goldenpath/dev/backstage/secrets" = {
    description = "Backstage sensitive config (GitHub Token, OIDC)"
    metadata = {
      id    = "SEC-BACKSTAGE-MAIN"
      owner = "platform-team"
      risk  = "high"
    }
    read_principals        = []
    write_principals       = []
    break_glass_principals = []
  }
}

# Platform RDS Configuration
# Manage database size, engine, and application databases here.
rds_config = {
  enabled               = true # ENABLED for Dev
  identifier            = "goldenpath-platform-db"
  instance_class        = "db.t3.micro"
  engine_version        = "15.15"
  allocated_storage     = 20
  max_allocated_storage = 50
  multi_az              = false # Keep false for Dev/Cost
  deletion_protection   = false
  skip_final_snapshot   = true
  backup_retention_days = 7

  # Databases to create and secret names to generate
  application_databases = {
    "keycloak" = {
      database_name = "keycloak"
      username      = "keycloak_app"
    }
    "backstage" = {
      database_name = "backstage_plugin_catalog" # Backstage uses many DBs, starting with catalog
      username      = "backstage_app"
    }
  }
}


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
  # External Secrets Operator IRSA
  enable_eso_role               = true
  eso_role_name                 = "goldenpath-idp-eso-role"
  eso_service_account_namespace = "external-secrets"
  eso_service_account_name      = "external-secrets"
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
ecr_repositories = {}
