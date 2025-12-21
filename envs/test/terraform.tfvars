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
