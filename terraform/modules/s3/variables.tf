
variable "bucket-versioning" {
  type        = bool
  default = false
  description = "whether to enable bucket versioning"
}

variable "bucket_name" {
  type        = string
  description = "bucket name"
}


variable "tags" {
  type        = map(string)
}


variable "env" {
   type        = string
}


variable "s3_encryption" {
  type = string
  description = "encryption to use e.g SSE-S3, KMS"
  default = "aws:kms"
  validation {
    condition     = can(regex("^(AES256||aws:kms:ddsse||aws:kms)$", var.s3_encryption))
    error_message = "The encryption must be either AES256, aws:kms, aws:kms:dsse"
  }
}


variable "force_destroy" {
  description = "Force destroy the S3 bucket and its contents when destroying the Terraform resource"
  type        = bool
  default     = false
}

locals{
  versioning    = var.bucket-versioning == true ? "Enabled" : "Disabled"
}
