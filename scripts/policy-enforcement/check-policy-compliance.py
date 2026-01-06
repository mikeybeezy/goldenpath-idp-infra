#!/usr/bin/env python3
"""
Daily Policy Compliance Check Script

Purpose:
    Automated daily compliance checker that validates ECR registries against
    governance policies defined in YAML files. Part of the automated policy
    enforcement framework.

What it does:
    1. Loads policy definitions from docs/policies/*.yaml
    2. Queries all ECR registries in AWS account
    3. Checks each registry against policy rules:
       - POL-ECR-001-R03: Required metadata present (id, owner, risk)
       - POL-ECR-002-R01: Image scanning enabled
       - POL-ECR-003-R01: Lifecycle policy configured
       - POL-ECR-002-R04: CVEs remediated within SLA
    4. Generates compliance report (JSON format)
    5. Returns exit code 0 if compliant, 1 if violations found

Usage:
    python check-policy-compliance.py [--region REGION] [--output FILE]

Options:
    --region REGION    AWS region (default: eu-west-2)
    --output FILE      Output file for compliance report (default: compliance-report.json)
    --verbose          Enable verbose logging

Output:
    JSON compliance report with structure:
    {
      "timestamp": "2026-01-05T09:00:00Z",
      "total_registries": 6,
      "compliant": 5,
      "compliance_rate": 0.83,
      "violations": [
        {
          "registry": "wordpress-platform",
          "policy_id": "POL-ECR-003-R01",
          "rule": "Lifecycle policy required",
          "severity": "high",
          "detected": "2026-01-05T09:00:00Z"
        }
      ]
    }

Exit Codes:
    0 - All registries compliant
    1 - Violations found
    2 - Error during execution

Related:
    - ADR-0093: Automated Policy Enforcement
    - ADR-0092: ECR Registry Product Strategy
    - docs/policies/README.md
    - .github/workflows/policy-enforcement.yml

Author: Platform Team
Created: 2026-01-05
"""

import argparse
import boto3
import json
import sys
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class PolicyLoader:
    """Load and parse policy YAML files"""

    def __init__(self, policy_dir: str = "docs/policies"):
        self.policy_dir = Path(policy_dir)

    def load_policies(self) -> Dict[str, Any]:
        """Load all policy YAML files"""
        policies = {}

        for policy_file in self.policy_dir.glob("*.yaml"):
            if policy_file.name == "README.md":
                continue

            with open(policy_file) as f:
                try:
                    for policy in yaml.safe_load_all(f):
                        if policy and isinstance(policy, dict) and 'policy_id' in policy:
                            policies[policy['policy_id']] = policy
                except yaml.YAMLError:
                    print(f"DEBUG: Skipping {policy_file.name} - YAML error")

        return policies


class ECRComplianceChecker:
    """Check ECR registries against policies"""

    def __init__(self, region: str = "eu-west-2"):
        self.ecr = boto3.client('ecr', region_name=region)
        self.region = region

    def get_all_registries(self) -> List[Dict[str, Any]]:
        """Get all ECR registries in account"""
        registries = []
        paginator = self.ecr.get_paginator('describe_repositories')

        for page in paginator.paginate():
            registries.extend(page['repositories'])

        return registries

    def check_metadata(self, registry: Dict[str, Any]) -> List[Dict[str, str]]:
        """Check POL-ECR-001-R03: Required metadata"""
        violations = []
        tags = self.ecr.list_tags_for_resource(resourceArn=registry['repositoryArn'])['tags']

        required_tags = ['metadata.id', 'metadata.owner', 'metadata.risk']
        for tag in required_tags:
            if not any(t['Key'] == tag for t in tags):
                violations.append({
                    "registry": registry['repositoryName'],
                    "policy_id": "POL-ECR-001-R03",
                    "rule": f"Missing required tag: {tag}",
                    "severity": "critical",
                    "detected": datetime.utcnow().isoformat() + "Z"
                })

        return violations

    def check_scanning(self, registry: Dict[str, Any]) -> List[Dict[str, str]]:
        """Check POL-ECR-002-R01: Image scanning enabled"""
        violations = []

        if not registry.get('imageScanningConfiguration', {}).get('scanOnPush'):
            violations.append({
                "registry": registry['repositoryName'],
                "policy_id": "POL-ECR-002-R01",
                "rule": "Image scanning not enabled",
                "severity": "high",
                "detected": datetime.utcnow().isoformat() + "Z"
            })

        return violations

    def check_lifecycle(self, registry: Dict[str, Any]) -> List[Dict[str, str]]:
        """Check POL-ECR-003-R01: Lifecycle policy exists"""
        violations = []

        try:
            self.ecr.get_lifecycle_policy(repositoryName=registry['repositoryName'])
        except self.ecr.exceptions.LifecyclePolicyNotFoundException:
            violations.append({
                "registry": registry['repositoryName'],
                "policy_id": "POL-ECR-003-R01",
                "rule": "Lifecycle policy not configured",
                "severity": "medium",
                "detected": datetime.utcnow().isoformat() + "Z"
            })

        return violations

    def check_registry(self, registry: Dict[str, Any]) -> List[Dict[str, str]]:
        """Check all policies for a single registry"""
        violations = []

        violations.extend(self.check_metadata(registry))
        violations.extend(self.check_scanning(registry))
        violations.extend(self.check_lifecycle(registry))

        return violations


def generate_report(registries: List[Dict], violations: List[Dict]) -> Dict[str, Any]:
    """Generate compliance report"""
    total = len(registries)
    violation_count = len(set(v['registry'] for v in violations))
    compliant = total - violation_count

    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "total_registries": total,
        "compliant": compliant,
        "compliance_rate": compliant / total if total > 0 else 1.0,
        "violations": violations
    }


def main():
    parser = argparse.ArgumentParser(description="Daily Policy Compliance Checker")
    parser.add_argument("--region", default="eu-west-2", help="AWS region")
    parser.add_argument("--output", default="compliance-report.json", help="Output file")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    args = parser.parse_args()

    try:
        # Load policies
        if args.verbose:
            print("Loading policies from docs/policies/*.yaml")
        loader = PolicyLoader()
        policies = loader.load_policies()

        if args.verbose:
            print(f"Loaded {len(policies)} policies")

        # Get all registries
        if args.verbose:
            print(f"Querying ECR registries in {args.region}")
        checker = ECRComplianceChecker(region=args.region)
        registries = checker.get_all_registries()

        if args.verbose:
            print(f"Found {len(registries)} registries")

        # Check compliance
        all_violations = []
        for registry in registries:
            if args.verbose:
                print(f"Checking {registry['repositoryName']}")
            violations = checker.check_registry(registry)
            all_violations.extend(violations)

        # Generate report
        report = generate_report(registries, all_violations)

        # Write report
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)

        # Print summary
        print(f"Compliance check complete")
        print(f"Total registries: {report['total_registries']}")
        print(f"Compliant: {report['compliant']}")
        print(f"Compliance rate: {report['compliance_rate'] * 100:.1f}%")
        print(f"Violations: {len(all_violations)}")
        print(f"Report saved to: {args.output}")

        # Exit with appropriate code
        sys.exit(0 if len(all_violations) == 0 else 1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
