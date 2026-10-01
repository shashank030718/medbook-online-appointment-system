variable "db_username" {
  description = "RDS database username"
  type        = string
  default     = "medbookadmin"
}

variable "db_password" {
  description = "RDS database password"
  type        = string
  sensitive   = true
}