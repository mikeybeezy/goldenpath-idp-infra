output "argocd_helm_release_status" {
  description = "Status of the ArgoCD Helm release."
  value       = helm_release.argocd.status
}

output "argocd_helm_release_version" {
  description = "Version of the ArgoCD Helm chart installed."
  value       = helm_release.argocd.version
}
