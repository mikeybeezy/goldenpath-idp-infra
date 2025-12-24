environment = "staging"
name_prefix = "goldenpath-staging"
vpc_cidr    = "10.2.0.0/16"

public_subnets = [
  {
    name              = "goldenpath-staging-public-a"
    cidr_block        = "10.2.1.0/24"
    availability_zone = "eu-west-2a"
  },
  {
    name              = "goldenpath-staging-public-b"
    cidr_block        = "10.2.2.0/24"
    availability_zone = "eu-west-2b"
  }
]

private_subnets = [
  {
    name              = "goldenpath-staging-private-a"
    cidr_block        = "10.2.11.0/24"
    availability_zone = "eu-west-2a"
  },
  {
    name              = "goldenpath-staging-private-b"
    cidr_block        = "10.2.12.0/24"
    availability_zone = "eu-west-2b"
  }
]

common_tags = {
  Project = "goldenpath-idp"
  Owner   = "platform-team"
}

# Base EC2 compute (disabled by default; set enabled = true to provision)
compute_config = {
  enabled                       = false
  name                          = "goldenpath-staging-app"
  ami_id                        = "ami-0a0ff88d0f3f85a14"
  instance_type                 = "t3.micro"
  subnet_type                   = "private"
  additional_security_group_ids = []
  ssh_key_name                  = null
  user_data                     = null
  iam_instance_profile          = null
  network_interface_description = "Golden Path staging instance"
  root_volume_size              = 20
  root_volume_type              = "gp3"
  root_volume_encrypted         = true
}

# eks_config = {
#   enabled      = true
#   cluster_name = "goldenpath-staging-eks"
#   version      = "1.29"
#   node_group = {
#     name           = "staging-default"
#     min_size       = 1
#     max_size       = 3
#     desired_size   = 2
#     instance_types = ["t3.medium"]
#     disk_size      = 20
#     capacity_type  = "ON_DEMAND"
#   }
# }

# Bootstrap defaults (used when EKS is enabled).
bootstrap_mode = true
enable_ssh_break_glass = false
