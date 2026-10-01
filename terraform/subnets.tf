resource "aws_subnet" "public_1" {
  vpc_id                  = aws_vpc.medbook.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "ap-south-1a"
  map_public_ip_on_launch = true

  tags = {
    Name = "medbook-public-1"
  }
}

resource "aws_subnet" "public_2" {
  vpc_id                  = aws_vpc.medbook.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "ap-south-1b"
  map_public_ip_on_launch = true

  tags = {
    Name = "medbook-public-2"
  }
}

resource "aws_subnet" "private_1" {
  vpc_id            = aws_vpc.medbook.id
  cidr_block        = "10.0.11.0/24"
  availability_zone = "ap-south-1a"

  tags = {
    Name = "medbook-private-1"
  }
}

resource "aws_subnet" "private_2" {
  vpc_id            = aws_vpc.medbook.id
  cidr_block        = "10.0.12.0/24"
  availability_zone = "ap-south-1b"

  tags = {
    Name = "medbook-private-2"
  }
}