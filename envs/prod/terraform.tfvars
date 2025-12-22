environment = "prod"
name_prefix = "goldenpath-prod"
vpc_cidr    = "10.3.0.0/16"

public_subnets = [
  {
    name              = "goldenpath-prod-public-a"
    cidr_block        = "10.3.1.0/24"
    availability_zone = "eu-west-2a"
  },
  {
    name              = "goldenpath-prod-public-b"
    cidr_block        = "10.3.2.0/24"
    availability_zone = "eu-west-2b"
  }
]

private_subnets = [
  {
    name              = "goldenpath-prod-private-a"
    cidr_block        = "10.3.11.0/24"
    availability_zone = "eu-west-2a"
  },
  {
    name              = "goldenpath-prod-private-b"
    cidr_block        = "10.3.12.0/24"
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
  name                          = "goldenpath-prod-app"
  ami_id                        = "ami-0a0ff88d0f3f85a14"
  instance_type                 = "t3.small"
  subnet_type                   = "private"
  additional_security_group_ids = []
  ssh_key_name                  = null
  user_data                     = null
  iam_instance_profile          = null
  network_interface_description = "Golden Path prod instance"
  root_volume_size              = 30
  root_volume_type              = "gp3"
  root_volume_encrypted         = true
}

# eks_config = {
#   enabled      = true
#   cluster_name = "goldenpath-prod-eks"
#   version      = "1.29"
#   node_group = {
#     name           = "prod-default"
#     min_size       = 2
#     max_size       = 4
#     desired_size   = 2
#     instance_types = ["m5.large"]
#     disk_size      = 40
#     capacity_type  = "ON_DEMAND"
#   }
# }
