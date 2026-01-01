variable "argocd_version" {
  description = "Version of the ArgoCD Helm chart to install."
  type        = string
  default     = "5.46.7" # Pinned stable version
}

variable "path_to_app_manifests" {
  description = "Path to the directory containing ArgoCD Application manifests (YAMLs) to verify/bootstrap."
  type        = string
  default     = ""
}

variable "tags" {
  description = "A map of tags to add to all resources."
  type        = map(string)
  default     = {}
}
