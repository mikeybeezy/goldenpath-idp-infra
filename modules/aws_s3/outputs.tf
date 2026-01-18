output "bucket_id" {
  description = "S3 bucket name."
  value       = aws_s3_bucket.this.id
}

output "bucket_arn" {
  description = "S3 bucket ARN."
  value       = aws_s3_bucket.this.arn
}

output "cost_alert_arn" {
  description = "CloudWatch alarm ARN for cost alert (if enabled)."
  value       = length(aws_cloudwatch_metric_alarm.cost_alert) > 0 ? aws_cloudwatch_metric_alarm.cost_alert[0].arn : null
}
