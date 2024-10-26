output "role_arn" {
  description = "iam role arn "
  value       = aws_iam_role.this.arn
}

output "role_id" {
  description = "Name of the role"
  value       = aws_iam_role.this.id
}


output "analyzer_arn" {
   description = "ARN of the Analyzer"
  value = aws_accessanalyzer_analyzer.account_level_analyzer.arn

}
