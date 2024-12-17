variable "s3_iam_role" {
  type    = string
  default = "SnowflakeIntegrationRole"
  description = "The name of the  AWS role"
}


variable "principal" {
  type        = string
  description = "arn of principal to assume role"
}

variable "snowflake_external_id" {
  type        = string
  description = "snowflake storage integration external id"
}


variable "bucket_tag" {
  type        = map(string)
}

variable "snowflake_bucket" {
  type        = string
  description = "bucket to map to snowflake stage"
}

variable "state_bucket" {
  type        = string
  description = "bucket to store the terraform state"
}

variable "ddb_table_name" {
  type        = string
  description = "ddb table for state locking"
}


variable "env" {
   type        = string
}
