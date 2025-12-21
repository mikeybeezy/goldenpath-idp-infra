environment = "staging"
name_prefix = "goldenpath-staging"
vpc_cidr    = "10.2.0.0/16"

public_subnets = [
  {
    name              = "goldenpath-staging-public-a"
    cidr_block        = "10.2.1.0/24"
    availability_zone = "us-east-1a"
  },
  {
    name              = "goldenpath-staging-public-b"
    cidr_block        = "10.2.2.0/24"
    availability_zone = "us-east-1b"
  }
]

private_subnets = [
  {
    name              = "goldenpath-staging-private-a"
    cidr_block        = "10.2.11.0/24"
    availability_zone = "us-east-1a"
  },
  {
    name              = "goldenpath-staging-private-b"
    cidr_block        = "10.2.12.0/24"
    availability_zone = "us-east-1b"
  }
]

common_tags = {
  Project = "goldenpath-idp"
  Owner   = "platform-team"
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
