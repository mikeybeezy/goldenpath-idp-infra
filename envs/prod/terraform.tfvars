environment = "prod"
name_prefix = "goldenpath-prod"
vpc_cidr    = "10.3.0.0/16"

public_subnets = [
  {
    name              = "goldenpath-prod-public-a"
    cidr_block        = "10.3.1.0/24"
    availability_zone = "us-east-1a"
  },
  {
    name              = "goldenpath-prod-public-b"
    cidr_block        = "10.3.2.0/24"
    availability_zone = "us-east-1b"
  }
]

private_subnets = [
  {
    name              = "goldenpath-prod-private-a"
    cidr_block        = "10.3.11.0/24"
    availability_zone = "us-east-1a"
  },
  {
    name              = "goldenpath-prod-private-b"
    cidr_block        = "10.3.12.0/24"
    availability_zone = "us-east-1b"
  }
]

common_tags = {
  Project = "goldenpath-idp"
  Owner   = "platform-team"
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
