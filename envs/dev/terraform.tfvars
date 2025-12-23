environment = "dev"
name_prefix = "goldenpath-dev"
vpc_cidr    = "10.0.0.0/16"

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

eks_config = {
  enabled      = true
  cluster_name = "goldenpath-dev-eks"
  version      = "1.29"
  node_group = {
    name           = "dev-default"
    min_size       = 1
    max_size       = 2
    desired_size   = 1
    instance_types = ["t3.medium"]
    disk_size      = 20
    capacity_type  = "ON_DEMAND"
    update_config = {
      max_unavailable = 1
    }
  }
}



# terraform {
#   # Assumes s3 bucket and dynamo DB table already set up
#   # See /code/03-basics/aws-backend
#   backend "s3" {
#     bucket         = "devops-initiative-state"
#     key            = "devops-initiatve/web-app/terraform.tfstate"
#     region         = "eu-west-2"
#     dynamodb_table = "state-lock"
#     encrypt        = true
#   }

#   required_providers {
#     aws = {
#       source  = "hashicorp/aws"
#       version = "~> 3.0"
#     }
#   }
# }

# provider "aws" {
#   region = "eu-west-2"
# }

# resource "aws_instance" "instance_1" {
#   ami           = "ami-0a0ff88d0f3f85a14" # Ubuntu 20.04 LTS // eu-west-2
#   instance_type = var.instance_type
#   subnet_id     = data.aws_subnet.subnet_id_b.id
#   depends_on = [
#     aws_s3_bucket.bucket_blaster2caletifc
#   ]
