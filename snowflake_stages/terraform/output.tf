output "snowflake_bucket_arn" {
  value = module.snowflake_s3_bucket.s3_bucket_arn
}

output "snowflake_iam_role_arn" {
  value = module.snowflake_iam.role_arn
}

output "access_analyzer_arn" {
  value = module.snowflake_iam.analyzer_arn
}

output "state_bucket_arn" {
  value = module.state_s3_bucket.s3_bucket_arn
}


output "state_ddb_arn" {
  description = "ddb table arn"
  value       = module.state_ddb_lock.ddb_arn
}

output "state_ddb_attributes" {
  description = "ddb table attributes"
  value       = module.state_ddb_lock.ddb_attributes
}
