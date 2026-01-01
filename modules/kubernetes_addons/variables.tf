variable "argocd_version" {
  description = "Version of the ArgoCD Helm chart to install."
  type        = string
  default     = "5.46.7" # Pinned stable version
}

variable "tags" {
  description = "A map of tags to add to all resources."
  type        = map(string)
  default     = {}
}
