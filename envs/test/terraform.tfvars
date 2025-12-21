environment = "test"
name_prefix = "goldenpath-test"
vpc_cidr    = "10.1.0.0/16"

public_subnets = [
  {
    name              = "goldenpath-test-public-a"
    cidr_block        = "10.1.1.0/24"
    availability_zone = "us-east-1a"
  },
  {
    name              = "goldenpath-test-public-b"
    cidr_block        = "10.1.2.0/24"
    availability_zone = "us-east-1b"
  }
]

private_subnets = [
  {
    name              = "goldenpath-test-private-a"
    cidr_block        = "10.1.11.0/24"
    availability_zone = "us-east-1a"
  },
  {
    name              = "goldenpath-test-private-b"
    cidr_block        = "10.1.12.0/24"
    availability_zone = "us-east-1b"
  }
]

common_tags = {
  Project = "goldenpath-idp"
  Owner   = "platform-team"
}

# eks_config = {
#   enabled      = true
#   cluster_name = "goldenpath-test-eks"
#   version      = "1.29"
#   node_group = {
#     name           = "test-default"
#     min_size       = 1
#     max_size       = 2
#     desired_size   = 1
#     instance_types = ["t3.medium"]
#     disk_size      = 20
#     capacity_type  = "ON_DEMAND"
#   }
# }
