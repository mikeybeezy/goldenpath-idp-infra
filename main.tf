#--------------------------provider------------------------------------------------------
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}






#---------------------------AWS_VPC------------------------------------------------------




#--------------------------AWS_IGW attached to VPC ---------------------------------------


#--------------------------AWS_IGW attached to VPC ---------------------------------------



#--------------------------AWS_route_table attached to VPC ---------------------------------------


#--------------------------AWS_route_table attached to Internet Gateway ---------------------------------------



#--------------------------AWS_Subnet attached to Route Table ---------------------------------------




#--------------------------AWS_Security Group attached to AWS_VPC -----------------------------




#--------------------------AWS_NIC attached to AWS INSTANCE-----------------------------




#--------------------------AWS_ INSTANCE -----------------------------





# vpc.tf
resource "aws_vpc" "main" { ... }

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.main.id
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route { cidr_block = "0.0.0.0/0"; gateway_id = aws_internet_gateway.this.id }
}

resource "aws_route_table_association" "public" {
  route_table_id = aws_route_table.public.id
  subnet_id      = aws_subnet.public.id
}

resource "aws_subnet" "public" { ... }

# security.tf
resource "aws_security_group" "instance" {
  vpc_id = aws_vpc.main.id
  ingress { ... }
  egress { ... }
}

# compute.tf
resource "aws_network_interface" "instance" {
  subnet_id       = aws_subnet.public.id
  security_groups = [aws_security_group.instance.id]
}

resource "aws_instance" "app" {
  ami           = var.ami_id
  instance_type = var.instance_type
  network_interface {
    network_interface_id = aws_network_interface.instance.id
    device_index         = 0
  }
}
