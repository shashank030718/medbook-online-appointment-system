resource "aws_cloudwatch_log_group" "medbook" {
  name              = "/ecs/medbook"
  retention_in_days = 7

  tags = {
    Name = "medbook-cloudwatch-logs"
  }
}