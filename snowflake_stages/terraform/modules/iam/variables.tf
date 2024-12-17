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


variable "bucket_arn" {
  type        = string
  description = "arn of bucket to apply permissions on"
}

