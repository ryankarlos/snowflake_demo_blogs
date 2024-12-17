variable "ddb_table_name" {
  type        = string
  description = "DDB table name"
}


variable "attributes" {
  description = "dynamodb table attributes"
  type        = map(string)
  default     = {
    name = "LockID"
    type = "S"
  }
}

variable "tags" {
  type        = map(string)
  default     = {
    responsible_team  = "DSAI"
  }
}


variable "billing_mode" {
  description = "Controls how you are billed for read/write throughput and how you manage capacity. The valid values are PROVISIONED or PAY_PER_REQUEST"
  type        = string
  default     = "PAY_PER_REQUEST"
}

variable "write_capacity" {
  description = "The number of write units for this table. If the billing_mode is PROVISIONED, this field should be greater than 0"
  type        = number
  default     = null
}

variable "read_capacity" {
  description = "The number of read units for this table. If the billing_mode is PROVISIONED, this field should be greater than 0"
  type        = number
  default     = null
}
