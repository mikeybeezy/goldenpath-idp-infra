environment = "dev"
name_prefix = "goldenpath-dev"
vpc_cidr    = "10.0.0.0/16"

public_subnets = [
  {
    name              = "goldenpath-dev-public-a"
    cidr_block        = "10.0.1.0/24"
    availability_zone = "us-east-1a"
  },
  {
    name              = "goldenpath-dev-public-b"
    cidr_block        = "10.0.2.0/24"
    availability_zone = "us-east-1b"
  }
]

private_subnets = [
  {
    name              = "goldenpath-dev-private-a"
    cidr_block        = "10.0.11.0/24"
    availability_zone = "us-east-1a"
  },
  {
    name              = "goldenpath-dev-private-b"
    cidr_block        = "10.0.12.0/24"
    availability_zone = "us-east-1b"
  }
]

common_tags = {
  Project = "goldenpath-idp"
  Owner   = "platform-team"
}
