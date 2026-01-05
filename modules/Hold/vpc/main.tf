
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  instance_tenancy     = "default"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(
    {
      Name        = var.vpc_tag
      Environment = var.environment
    },
    var.tags,
  )
}

resource "aws_internet_gateway" "this" {
  count = var.create_internet_gateway && var.existing_internet_gateway_id == "" ? 1 : 0

  vpc_id = aws_vpc.main.id

  tags = merge(
    var.tags,
    {
      Name        = "${var.vpc_tag}-igw"
      Environment = var.environment
    },
  )
}

locals {
  internet_gateway_id = var.existing_internet_gateway_id != "" ? var.existing_internet_gateway_id : (
    var.create_internet_gateway && length(aws_internet_gateway.this) > 0 ? aws_internet_gateway.this[0].id : null
  )
}

resource "aws_route_table" "public" {
  count  = var.create_public_route_table ? 1 : 0
  vpc_id = aws_vpc.main.id

  dynamic "route" {
    for_each = local.internet_gateway_id != null ? [local.internet_gateway_id] : []
    content {
      cidr_block = var.public_route_cidr_block
      gateway_id = route.value
    }
  }

  tags = merge(
    var.tags,
    {
      Name        = var.public_route_table_name
      Environment = var.environment
    },
  )
}
