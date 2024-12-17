resource "aws_iam_role" "this" {
  name = var.s3_iam_role
  path = "/"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          AWS = var.principal
        }
        Condition = {
          StringEquals = {
            "sts:ExternalId" = var.snowflake_external_id
          }
        }
      }
    ]
  })
}

data "aws_iam_policy_document" "s3_policy_doc" {
  statement {
    sid       = "S3ReadWritePerms"
    effect    = "Allow"
    resources = ["${var.bucket_arn}/*"]

    actions = [
      "s3:PutObject",
      "s3:GetObject",
      "s3:GetObjectVersion",
      "s3:DeleteObject",
      "s3:DeleteObjectVersion"
    ]
  }

  statement {
    sid       = "S3ListPerms"
    effect    = "Allow"
    resources = [var.bucket_arn]

    actions = ["s3:ListBucket", "s3:GetBucketLocation"]

    condition {
      test     = "StringLike"
      variable = "s3:prefix"
      values   = ["*"]
    }
  }
}


resource "aws_iam_role_policy" "s3_policy" {
  name = "snowflake_s3_policy"
  role = aws_iam_role.this.id

  policy = data.aws_iam_policy_document.s3_policy_doc.json
}

resource "aws_accessanalyzer_analyzer" "account_level_analyzer" {
  analyzer_name = "account_analyzer"
}
