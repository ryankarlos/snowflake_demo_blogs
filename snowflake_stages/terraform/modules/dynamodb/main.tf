resource "aws_dynamodb_table" "dynamodb-terraform-lock" {
   name = var.ddb_table_name
   hash_key = var.attributes.name
   billing_mode   = var.billing_mode
   read_capacity  = var.read_capacity
   write_capacity = var.write_capacity

   attribute {
      name = var.attributes.name
      type = var.attributes.type
   }

}
