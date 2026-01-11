#!/usr/bin/env python3
"""
Purpose: Process SecretRequest manifests into Infrastructure and K8s configuration.
Achievement: Translates declarative secret intent into AWS Secrets Manager (via Terraform)
             and Kubernetes projection (via ExternalSecret).
Relates-To: how-it-works/SECRET_REQUEST_FLOW.md
"""
import os
import sys
import yaml
import argparse
from datetime import datetime

class SecretProcessor:
    def __init__(self, request_file):
        self.request_file = request_file
        self.data = self._load_request()
        self.spec = self.data.get('spec', {})
        self.metadata = self.data.get('metadata', {})
        self.env = self.metadata.get('environment')
        self.service = self.metadata.get('service')
        self.id = self.metadata.get('id')
        self.name = self.metadata.get('name')

    def _load_request(self):
        with open(self.request_file, 'r') as f:
            return yaml.safe_load(f)

    def update_tfvars(self):
        """Injects the secret into the environment's terraform.tfvars."""
        tfvars_path = f"envs/{self.env}/terraform.tfvars"
        
        # Determine the unique key for the secret in the HCL map
        # Pattern: <service>-<name>
        secret_key = f"{self.service}-{self.name}"
        
        entry = f"""
  "{secret_key}" = {{
    description = "Managed secret for {self.service} in {self.env}"
    metadata = {{
      id    = "{self.id}"
      owner = "{self.metadata.get('owner', 'unknown')}"
      risk  = "{self.spec.get('riskTier', 'medium')}"
    }}
  }}
"""
        
        if not os.path.exists(tfvars_path):
            print(f"⚠️ {tfvars_path} not found. Skipping tfvars update.")
            return

        with open(tfvars_path, "r") as f:
            lines = f.readlines()

        # Find the start of app_secrets block
        start_idx = -1
        for i, line in enumerate(lines):
            if line.strip().startswith("app_secrets = {"):
                start_idx = i
                break

        if start_idx == -1:
            # Append new block if not found
            with open(tfvars_path, "a") as f:
                f.write(f"\n# Secret Catalog\napp_secrets = {{\n{entry}}}\n")
            print(f"✅ Created new app_secrets block in {tfvars_path}")
            return

        # Find closing brace
        insert_idx = -1
        brace_count = 0
        for i, line in enumerate(lines):
            if i < start_idx: continue
            brace_count += line.count("{")
            brace_count -= line.count("}")
            if brace_count == 0:
                insert_idx = i
                break

        if insert_idx != -1:
            # Check if entry already exists
            content = "".join(lines)
            if f'"{secret_key}"' in content:
                print(f"⚠️ Secret {secret_key} already in tfvars. Skipping.")
                return

            lines.insert(insert_idx, entry)
            with open(tfvars_path, "w") as f:
                f.writelines(lines)
            print(f"✅ Injected secret {secret_key} into {tfvars_path}")
        else:
            print("❌ Failed to parse tfvars block.")
            sys.exit(1)

    def generate_external_secret(self):
        """Generates the ExternalSecret manifest for ESO."""
        output_dir = f"gitops/manifests/secrets/{self.env}"
        os.makedirs(output_dir, exist_ok=True)
        
        # The AWS secret path is standardized: /<env>/<service>/<name>
        aws_path = f"goldenpath/{self.env}/{self.service}/{self.name}"
        
        manifest = {
            "apiVersion": "external-secrets.io/v1beta1",
            "kind": "ExternalSecret",
            "metadata": {
                "name": f"{self.service}-{self.name}-sync",
                "namespace": self.spec.get('access', {}).get('namespace', self.service),
                "labels": {
                    "goldenpath.idp/id": self.id,
                    "platform.idp/service": self.service
                }
            },
            "spec": {
                "refreshInterval": "1h",
                "secretStoreRef": {
                    "name": "aws-secretsmanager",
                    "kind": "ClusterSecretStore"
                },
                "target": {
                    "name": self.spec.get('access', {}).get('k8sSecretName', f"{self.service}-{self.name}"),
                    "creationPolicy": "Owner"
                },
                "dataFrom": [
                    {
                        "extract": {
                            "key": aws_path
                        }
                    }
                ]
            }
        }
        
        output_file = f"{output_dir}/{self.service}-{self.name}.yaml"
        with open(output_file, 'w') as f:
            yaml.dump(manifest, f, default_flow_style=False)
        
        print(f"✅ Generated ExternalSecret manifest: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Process a SecretRequest.")
    parser.add_argument("--request-file", required=True, help="Path to the SecretRequest YAML")
    parser.add_argument("--tfvars", action="store_true", help="Update terraform.tfvars")
    parser.add_argument("--manifest", action="store_true", help="Generate K8s manifests")
    
    args = parser.parse_args()
    
    processor = SecretProcessor(args.request_file)
    
    if args.tfvars:
        processor.update_tfvars()
    
    if args.manifest:
        processor.generate_external_secret()

if __name__ == "__main__":
    main()
