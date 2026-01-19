output "secret_arn" {
  description = "The ARN of the secret (created or adopted)"
  value       = local.secret_arn
}

output "secret_id" {
  description = "The ID of the secret (created or adopted)"
  value       = local.secret_id
}

output "secret_name" {
  description = "The name of the secret"
  value       = var.name
}

output "adopted" {
  description = "Whether an existing secret was adopted (true) or a new one created (false)"
  value       = local.secret_exists
}
