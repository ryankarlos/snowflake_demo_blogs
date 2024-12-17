resource "aws_s3_bucket" "this" {
  bucket = var.bucket_name

  tags = {
    environment       = var.env
    responsible_team  = var.tags.responsible_team
  }

  force_destroy = var.force_destroy
}


resource "aws_s3_bucket_acl" "acl" {
  bucket = aws_s3_bucket.this.id
  acl    = "private"
  depends_on = [aws_s3_bucket_ownership_controls.ownership]
}


resource "aws_s3_bucket_versioning" "versioning" {
  bucket = aws_s3_bucket.this.id
  versioning_configuration {
    status = local.versioning
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "sse" {
  bucket = aws_s3_bucket.this.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = var.s3_encryption
    }
  }
}

resource "aws_s3_bucket_ownership_controls" "ownership" {
  bucket = aws_s3_bucket.this.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}


resource "aws_s3_bucket_policy" "enforce_ssl" {
  bucket = aws_s3_bucket.this.id
  policy = data.aws_iam_policy_document.bucket_policy.json
}

# https://repost.aws/knowledge-center/s3-bucket-policy-for-config-rule
data "aws_iam_policy_document" "bucket_policy" {
  statement {
    sid = "AllowSSLRequestsOnly"
    effect = "Deny"
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    actions = ["s3:*"]
    resources = [
      "${aws_s3_bucket.this.arn}",
      "${aws_s3_bucket.this.arn}/*"
    ]
    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }

}
