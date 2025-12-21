terraform {
  required_version = ">= 1.5.0"
}

locals {
  environment = "test"
  name_prefix = "goldenpath-${local.environment}"
  azs         = ["us-east-1a", "us-east-1b"]

  public_subnets = [
    {
      name              = "${local.name_prefix}-public-a"
      cidr_block        = "10.1.1.0/24"
      availability_zone = local.azs[0]
    },
    {
      name              = "${local.name_prefix}-public-b"
      cidr_block        = "10.1.2.0/24"
      availability_zone = local.azs[1]
    }
  ]

  private_subnets = [
    {
      name              = "${local.name_prefix}-private-a"
      cidr_block        = "10.1.11.0/24"
      availability_zone = local.azs[0]
    },
    {
      name              = "${local.name_prefix}-private-b"
      cidr_block        = "10.1.12.0/24"
      availability_zone = local.azs[1]
    }
  ]

  common_tags = {
    Environment = local.environment
    Project     = "goldenpath-idp"
    ManagedBy   = "terraform"
  }
}

module "vpc" {
  source = "../../modules/vpc"

  vpc_cidr = "10.1.0.0/16"
  vpc_tag  = "${local.name_prefix}-vpc"
  tags     = local.common_tags
}

module "subnets" {
  source = "../../modules/aws_subnet"

  vpc_id          = module.vpc.vpc_id
  public_subnets  = local.public_subnets
  private_subnets = local.private_subnets
  tags            = local.common_tags
}

module "public_route_table" {
  source = "../../modules/aws_route_table"

  vpc_id                 = module.vpc.vpc_id
  name                   = "${local.name_prefix}-public-rt"
  gateway_id             = module.vpc.internet_gateway_id
  subnet_ids             = module.subnets.public_subnet_ids
  destination_cidr_block = "0.0.0.0/0"
  tags                   = local.common_tags
}

module "web_security_group" {
  source = "../../modules/aws_sg"

  name                     = "${local.name_prefix}-web-sg"
  vpc_id                   = module.vpc.vpc_id
  ingress_cidr_blocks      = ["0.0.0.0/0"]
  ingress_ipv6_cidr_blocks = ["::/0"]
  tags                     = local.common_tags
}
