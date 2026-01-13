
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

# -----------------------------------------------------------------------------
# VPC Endpoints (PrivateLink)
# -----------------------------------------------------------------------------

# S3 Gateway Endpoint (No cost, highly recommended for private subnets)
resource "aws_vpc_endpoint" "s3" {
  count             = var.enable_s3_endpoint ? 1 : 0
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.${var.aws_region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = var.private_route_table_ids

  tags = merge(
    var.tags,
    {
      Name        = "${var.vpc_tag}-s3-endpoint"
      Environment = var.environment
    },
  )
}

# Security Group for Interface Endpoints allows HTTPS from within VPC
resource "aws_security_group" "vpc_endpoints" {
  count       = var.enable_interface_endpoints ? 1 : 0
  name        = "${var.vpc_tag}-vpce-sg"
  description = "Security group for VPC Interface Endpoints"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [var.vpc_cidr]
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.vpc_tag}-vpce-sg"
      Environment = var.environment
    },
  )
}

# Dynamic Interface Endpoints (EC2, ECR, STS, Logs, SSM, etc.)
resource "aws_vpc_endpoint" "interface" {
  for_each            = var.enable_interface_endpoints ? toset(var.interface_endpoint_services) : []
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.aws_region}.${each.value}"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = var.private_subnet_ids
  security_group_ids  = [aws_security_group.vpc_endpoints[0].id]
  private_dns_enabled = true

  tags = merge(
    var.tags,
    {
      Name        = "${var.vpc_tag}-${each.value}-endpoint"
      Environment = var.environment
    },
  )
}
