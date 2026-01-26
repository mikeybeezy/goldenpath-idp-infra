# ---
# id: TFTEST-VPC-001
# type: terraform-test
# owner: platform-team
# status: active
# maturity: 1
# ---
# Terraform native tests for vpc module
# Run with: cd modules/vpc && terraform init && terraform test

# -----------------------------------------------------------------------------
# Mock Provider Configuration
# -----------------------------------------------------------------------------
mock_provider "aws" {}

# -----------------------------------------------------------------------------
# Variables Block - Shared test inputs
# -----------------------------------------------------------------------------
variables {
  vpc_cidr    = "10.0.0.0/16"
  vpc_tag     = "test-vpc"
  environment = "test"

  create_internet_gateway = true
  create_public_route_table = true
  public_route_cidr_block = "0.0.0.0/0"
  public_route_table_name = "test-public-rt"

  tags = {
    Project   = "goldenpath-idp"
    ManagedBy = "terraform"
  }
}

# -----------------------------------------------------------------------------
# Test: VPC CIDR Configuration
# -----------------------------------------------------------------------------
run "vpc_cidr_set" {
  command = plan

  assert {
    condition     = aws_vpc.main.cidr_block == var.vpc_cidr
    error_message = "VPC CIDR block should match var.vpc_cidr"
  }
}

# -----------------------------------------------------------------------------
# Test: VPC Default Settings
# -----------------------------------------------------------------------------
run "vpc_defaults" {
  command = plan

  assert {
    condition     = aws_vpc.main.instance_tenancy == "default"
    error_message = "VPC instance tenancy should be 'default'"
  }

  assert {
    condition     = aws_vpc.main.enable_dns_hostnames == true
    error_message = "DNS hostnames should be enabled"
  }

  assert {
    condition     = aws_vpc.main.enable_dns_support == true
    error_message = "DNS support should be enabled"
  }
}

# -----------------------------------------------------------------------------
# Test: VPC Tags
# -----------------------------------------------------------------------------
run "vpc_tags" {
  command = plan

  assert {
    condition     = lookup(aws_vpc.main.tags, "Name", "") == var.vpc_tag
    error_message = "VPC should have Name tag matching vpc_tag"
  }

  assert {
    condition     = lookup(aws_vpc.main.tags, "Environment", "") == var.environment
    error_message = "VPC should have Environment tag"
  }

  assert {
    condition     = lookup(aws_vpc.main.tags, "Project", "") == "goldenpath-idp"
    error_message = "VPC should have custom Project tag"
  }
}

# -----------------------------------------------------------------------------
# Test: Internet Gateway Created
# -----------------------------------------------------------------------------
run "internet_gateway_created" {
  command = plan

  assert {
    condition     = length(aws_internet_gateway.this) == 1
    error_message = "Internet Gateway should be created when create_internet_gateway is true"
  }
}

run "internet_gateway_tags" {
  command = plan

  assert {
    condition     = lookup(aws_internet_gateway.this[0].tags, "Name", "") == "${var.vpc_tag}-igw"
    error_message = "Internet Gateway should be named '{vpc_tag}-igw'"
  }

  assert {
    condition     = lookup(aws_internet_gateway.this[0].tags, "Environment", "") == var.environment
    error_message = "Internet Gateway should have Environment tag"
  }
}

# -----------------------------------------------------------------------------
# Test: Skip Internet Gateway When Disabled
# -----------------------------------------------------------------------------
run "skip_igw_when_disabled" {
  command = plan

  variables {
    create_internet_gateway = false
  }

  assert {
    condition     = length(aws_internet_gateway.this) == 0
    error_message = "Internet Gateway should NOT be created when create_internet_gateway is false"
  }
}

# -----------------------------------------------------------------------------
# Test: Use Existing Internet Gateway
# -----------------------------------------------------------------------------
run "use_existing_igw" {
  command = plan

  variables {
    create_internet_gateway      = true
    existing_internet_gateway_id = "igw-existing123"
  }

  assert {
    condition     = length(aws_internet_gateway.this) == 0
    error_message = "Should not create IGW when existing_internet_gateway_id is provided"
  }
}

# -----------------------------------------------------------------------------
# Test: Public Route Table Created
# -----------------------------------------------------------------------------
run "public_route_table_created" {
  command = plan

  assert {
    condition     = length(aws_route_table.public) == 1
    error_message = "Public route table should be created when create_public_route_table is true"
  }
}

run "public_route_table_tags" {
  command = plan

  assert {
    condition     = lookup(aws_route_table.public[0].tags, "Name", "") == var.public_route_table_name
    error_message = "Route table should have Name tag matching public_route_table_name"
  }

  assert {
    condition     = lookup(aws_route_table.public[0].tags, "Environment", "") == var.environment
    error_message = "Route table should have Environment tag"
  }
}

# -----------------------------------------------------------------------------
# Test: Skip Public Route Table When Disabled
# -----------------------------------------------------------------------------
run "skip_route_table_when_disabled" {
  command = plan

  variables {
    create_public_route_table = false
  }

  assert {
    condition     = length(aws_route_table.public) == 0
    error_message = "Public route table should NOT be created when create_public_route_table is false"
  }
}

# -----------------------------------------------------------------------------
# Test: Different CIDR Block
# -----------------------------------------------------------------------------
run "custom_cidr" {
  command = plan

  variables {
    vpc_cidr = "172.16.0.0/16"
  }

  assert {
    condition     = aws_vpc.main.cidr_block == "172.16.0.0/16"
    error_message = "VPC should use the custom CIDR block"
  }
}

# -----------------------------------------------------------------------------
# Test: No Environment Tag When Empty
# -----------------------------------------------------------------------------
run "empty_environment" {
  command = plan

  variables {
    environment = ""
  }

  assert {
    condition     = lookup(aws_vpc.main.tags, "Environment", "NOT_SET") == ""
    error_message = "Environment tag should be empty string when not set"
  }
}
