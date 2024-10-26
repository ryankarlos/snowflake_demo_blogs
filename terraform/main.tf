module "snowflake_s3_bucket" {
  source            = "./modules/s3"
  bucket_name       = var.snowflake_bucket
  env               = var.env
  tags = var.bucket_tag
}


module "state_s3_bucket" {
  source = "./modules/s3"
  bucket_name       = var.state_bucket
  env = var.env
  bucket-versioning =  true
  tags = var.bucket_tag
}



module "state_ddb_lock" {
  source            = "./modules/dynamodb"
  ddb_table_name = var.ddb_table_name

}

module "snowflake_iam" {
  source            = "./modules/iam"
  principal = var.principal
  snowflake_external_id = var.snowflake_external_id
  bucket_arn = module.snowflake_s3_bucket.s3_bucket_arn
  s3_iam_role = var.s3_iam_role
}
