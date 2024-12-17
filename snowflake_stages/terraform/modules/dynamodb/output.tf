output "ddb_arn" {
  description = "ddb table arn"
  value       = aws_dynamodb_table.dynamodb-terraform-lock.arn
}

output "ddb_attributes" {
  description = "ddb table attributes"
  value       = aws_dynamodb_table.dynamodb-terraform-lock.attribute
}

output "ddb_table_hash" {
  description = "ddb table hash key"
  value       = aws_dynamodb_table.dynamodb-terraform-lock.hash_key
}

output "ddb_billing_mode" {
  description = "ddb table billing mode e.g. provisioned or pay as you go"
  value       = aws_dynamodb_table.dynamodb-terraform-lock.billing_mode
}
