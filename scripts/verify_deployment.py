#!/usr/bin/env python3
"""
---
id: SCRIPT-0048
type: script
owner: platform-team
status: active
maturity: 2
dry_run:
  supported: false
  command_hint: N/A
test:
  runner: manual
  command: python3 scripts/verify_deployment.py --help
  evidence: declared
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
relates_to:
  - ADR-0148
  - CL-0121
  - RB-0029
---
"""

"""
EKS Single-Build Deployment Verification

Purpose:
    Verifies that EKS cluster and ArgoCD applications are healthy after
    Terraform deployment. Provides comprehensive health checks and scoring.

Usage:
    python3 scripts/verify_deployment.py --cluster <name> --region <region>
    python3 scripts/verify_deployment.py --cluster goldenpath-dev-eks --region us-east-1

Features:
    - Cluster connectivity verification
    - Node health checks
    - ArgoCD installation validation
    - Application sync status monitoring
    - Platform component health checks
    - Admin credentials retrieval
    - Health score calculation (0-100%)

Exit Codes:
    0: Verification successful (health >= 70%)
    1: Verification failed or critical error
"""

import sys
import subprocess
import json
import argparse
import base64
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class HealthStatus(Enum):
    """Health status levels"""
    EXCELLENT = "EXCELLENT"  # 90-100%
    GOOD = "GOOD"            # 70-89%
    DEGRADED = "DEGRADED"    # 50-69%
    CRITICAL = "CRITICAL"    # <50%


class Color:
    """ANSI color codes for terminal output"""
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    BLUE = '\033[0;34m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


@dataclass
class VerificationResult:
    """Result of a verification check"""
    name: str
    passed: bool
    message: str
    details: Optional[str] = None


class KubernetesClient:
    """Wrapper for kubectl commands"""

    @staticmethod
    def run_command(cmd: List[str], check: bool = True, capture_output: bool = True) -> subprocess.CompletedProcess:
        """Execute a command and return result"""
        try:
            result = subprocess.run(
                cmd,
                check=check,
                capture_output=capture_output,
                text=True,
                timeout=30
            )
            return result
        except subprocess.CalledProcessError as e:
            if check:
                raise
            return e
        except subprocess.TimeoutExpired as e:
            print(f"{Color.RED}Command timed out: {' '.join(cmd)}{Color.RESET}")
            raise

    @staticmethod
    def update_kubeconfig(cluster_name: str, region: str) -> bool:
        """Update kubeconfig for cluster access"""
        cmd = [
            'aws', 'eks', 'update-kubeconfig',
            '--name', cluster_name,
            '--region', region
        ]
        result = KubernetesClient.run_command(cmd, check=False)
        return result.returncode == 0

    @staticmethod
    def get_nodes() -> Tuple[int, int]:
        """Get node count and ready count"""
        cmd = ['kubectl', 'get', 'nodes', '--no-headers']
        result = KubernetesClient.run_command(cmd, check=False)

        if result.returncode != 0:
            return 0, 0

        lines = result.stdout.strip().split('\n')
        total = len([line for line in lines if line])
        ready = len([line for line in lines if 'Ready' in line and 'NotReady' not in line])

        return total, ready

    @staticmethod
    def get_pods(namespace: str, selector: Optional[str] = None) -> List[Dict]:
        """Get pods in namespace"""
        cmd = ['kubectl', 'get', 'pods', '-n', namespace, '-o', 'json']
        if selector:
            cmd.extend(['-l', selector])

        result = KubernetesClient.run_command(cmd, check=False)

        if result.returncode != 0:
            return []

        try:
            data = json.loads(result.stdout)
            return data.get('items', [])
        except json.JSONDecodeError:
            return []

    @staticmethod
    def get_applications(namespace: str = 'argocd') -> List[Dict]:
        """Get ArgoCD applications"""
        cmd = ['kubectl', 'get', 'applications', '-n', namespace, '-o', 'json']
        result = KubernetesClient.run_command(cmd, check=False)

        if result.returncode != 0:
            return []

        try:
            data = json.loads(result.stdout)
            return data.get('items', [])
        except json.JSONDecodeError:
            return []

    @staticmethod
    def get_secret(name: str, namespace: str, key: str) -> Optional[str]:
        """Get secret value"""
        cmd = [
            'kubectl', 'get', 'secret', name,
            '-n', namespace,
            '-o', f'jsonpath={{.data.{key}}}'
        ]
        result = KubernetesClient.run_command(cmd, check=False)

        if result.returncode != 0:
            return None

        try:
            return base64.b64decode(result.stdout).decode('utf-8')
        except Exception:
            return None

    @staticmethod
    def wait_for_pods(namespace: str, selector: str, timeout: int = 300) -> bool:
        """Wait for pods to be ready"""
        cmd = [
            'kubectl', 'wait', '--for=condition=Ready',
            f'--timeout={timeout}s',
            '-n', namespace,
            'pod', '-l', selector
        ]
        result = KubernetesClient.run_command(cmd, check=False)
        return result.returncode == 0


class DeploymentVerifier:
    """Main verification orchestrator"""

    def __init__(self, cluster_name: str, region: str):
        self.cluster_name = cluster_name
        self.region = region
        self.results: List[VerificationResult] = []
        self.k8s = KubernetesClient()

    def print_header(self, text: str):
        """Print section header"""
        print()
        print(f"{Color.BLUE}{'=' * 60}{Color.RESET}")
        print(f"{Color.BLUE}{text}{Color.RESET}")
        print(f"{Color.BLUE}{'=' * 60}{Color.RESET}")
        print()

    def print_banner(self):
        """Print welcome banner"""
        print(f"{Color.BLUE}")
        print("╔═══════════════════════════════════════════════════════════╗")
        print("║                                                           ║")
        print("║   Golden Path IDP - Deployment Verification               ║")
        print("║                                                           ║")
        print("╚═══════════════════════════════════════════════════════════╝")
        print(f"{Color.RESET}")
        print(f"{Color.BLUE}ℹ️  Cluster: {self.cluster_name}{Color.RESET}")
        print(f"{Color.BLUE}ℹ️  Region: {self.region}{Color.RESET}")
        print()

    def print_success(self, message: str):
        """Print success message"""
        print(f"{Color.GREEN}✅ {message}{Color.RESET}")

    def print_warning(self, message: str):
        """Print warning message"""
        print(f"{Color.YELLOW}⚠️  {message}{Color.RESET}")

    def print_error(self, message: str):
        """Print error message"""
        print(f"{Color.RED}❌ {message}{Color.RESET}")

    def print_info(self, message: str):
        """Print info message"""
        print(f"{Color.BLUE}ℹ️  {message}{Color.RESET}")

    def add_result(self, name: str, passed: bool, message: str, details: str = None):
        """Add verification result"""
        self.results.append(VerificationResult(name, passed, message, details))

    def verify_kubectl_config(self) -> bool:
        """Step 1: Configure kubectl"""
        self.print_header("Step 1: Configure kubectl")

        if self.k8s.update_kubeconfig(self.cluster_name, self.region):
            self.print_success(f"kubectl configured for cluster {self.cluster_name}")
            self.add_result("kubectl_config", True, "kubectl configured successfully")
            return True
        else:
            self.print_error("Failed to configure kubectl. Is the cluster accessible?")
            self.add_result("kubectl_config", False, "kubectl configuration failed")
            return False

    def verify_cluster_connectivity(self) -> bool:
        """Step 2: Verify cluster connectivity"""
        self.print_header("Step 2: Verify Cluster Connectivity")

        cmd = ['kubectl', 'cluster-info']
        result = self.k8s.run_command(cmd, check=False, capture_output=True)

        if result.returncode == 0:
            self.print_success("Cluster is accessible")
            self.add_result("cluster_connectivity", True, "Cluster accessible")

            # Show version info
            version_cmd = ['kubectl', 'version', '--short']
            version_result = self.k8s.run_command(version_cmd, check=False)
            if version_result.returncode == 0:
                print(version_result.stdout)

            return True
        else:
            self.print_error("Cannot connect to cluster")
            self.add_result("cluster_connectivity", False, "Cluster not accessible")
            return False

    def verify_nodes(self) -> bool:
        """Step 3: Check node status"""
        self.print_header("Step 3: Check Node Status")

        total_nodes, ready_nodes = self.k8s.get_nodes()

        if ready_nodes >= 3:
            self.print_success(f"{ready_nodes}/{total_nodes} nodes are Ready")
            self.add_result("node_health", True, f"{ready_nodes}/{total_nodes} nodes ready")

            # Show node details
            cmd = ['kubectl', 'get', 'nodes']
            self.k8s.run_command(cmd, check=False, capture_output=False)
            print()
            return True
        elif ready_nodes > 0:
            self.print_warning(f"Only {ready_nodes}/{total_nodes} nodes are Ready (expected at least 3)")
            self.add_result("node_health", False, f"Insufficient ready nodes: {ready_nodes}/{total_nodes}")

            cmd = ['kubectl', 'get', 'nodes']
            self.k8s.run_command(cmd, check=False, capture_output=False)
            print()
            return False
        else:
            self.print_error("No ready nodes found")
            self.add_result("node_health", False, "No ready nodes")
            return False

    def verify_argocd(self) -> Tuple[bool, int, int]:
        """Step 4: Check ArgoCD installation"""
        self.print_header("Step 4: Check ArgoCD Installation")

        # Check namespace exists
        cmd = ['kubectl', 'get', 'namespace', 'argocd']
        result = self.k8s.run_command(cmd, check=False, capture_output=True)

        if result.returncode != 0:
            self.print_error("ArgoCD namespace not found")
            self.add_result("argocd_namespace", False, "Namespace not found")
            return False, 0, 0

        self.print_success("ArgoCD namespace exists")

        # Check pods
        pods = self.k8s.get_pods('argocd')
        total_pods = len(pods)
        running_pods = len([p for p in pods if p.get('status', {}).get('phase') == 'Running'])

        if running_pods >= 5:
            self.print_success(f"ArgoCD is running ({running_pods}/{total_pods} pods Running)")
            self.add_result("argocd_pods", True, f"{running_pods}/{total_pods} pods running")
        else:
            self.print_warning(f"ArgoCD may not be fully ready ({running_pods}/{total_pods} pods Running)")
            self.add_result("argocd_pods", False, f"Insufficient running pods: {running_pods}/{total_pods}")

        # Show pod details
        cmd = ['kubectl', 'get', 'pods', '-n', 'argocd']
        self.k8s.run_command(cmd, check=False, capture_output=False)
        print()

        return running_pods >= 5, total_pods, running_pods

    def verify_applications(self) -> Tuple[bool, int, int, int]:
        """Step 5: Check ArgoCD Applications"""
        self.print_header("Step 5: Check ArgoCD Applications")

        apps = self.k8s.get_applications('argocd')
        total_apps = len(apps)

        if total_apps == 0:
            self.print_warning("No ArgoCD Applications found")
            self.print_info("Applications may still be deploying")
            self.add_result("argocd_apps", False, "No applications found")
            return False, 0, 0, 0

        self.print_success(f"Found {total_apps} ArgoCD Applications")
        print()

        # Analyze application status
        synced_count = 0
        healthy_count = 0

        print(f"{'NAME':<30} {'SYNC':<15} {'HEALTH':<15}")
        print("-" * 60)

        for app in apps:
            name = app.get('metadata', {}).get('name', 'unknown')
            sync_status = app.get('status', {}).get('sync', {}).get('status', 'Unknown')
            health_status = app.get('status', {}).get('health', {}).get('status', 'Unknown')

            print(f"{name:<30} {sync_status:<15} {health_status:<15}")

            if sync_status == 'Synced':
                synced_count += 1
            if health_status == 'Healthy':
                healthy_count += 1

        print()

        if synced_count == total_apps and healthy_count == total_apps:
            self.print_success(f"All {total_apps} applications are Synced and Healthy")
            self.add_result("app_sync", True, f"All {total_apps} apps synced and healthy")
            return True, total_apps, synced_count, healthy_count
        else:
            self.print_warning(f"{synced_count}/{total_apps} Synced, {healthy_count}/{total_apps} Healthy")
            self.print_info("Applications may still be syncing in the background")
            self.add_result("app_sync", False, f"Not all apps synced: {synced_count}/{total_apps}")
            return False, total_apps, synced_count, healthy_count

    def verify_platform_components(self) -> Dict[str, bool]:
        """Step 6: Check critical platform components"""
        self.print_header("Step 6: Check Critical Platform Components")

        components = {
            'metrics_server': ('kube-system', 'k8s-app=metrics-server', 'Metrics Server'),
            'lb_controller': ('kube-system', 'app.kubernetes.io/name=aws-load-balancer-controller', 'AWS Load Balancer Controller'),
            'cluster_autoscaler': ('kube-system', 'app.kubernetes.io/name=aws-cluster-autoscaler', 'Cluster Autoscaler'),
            'image_updater': ('argocd', 'app.kubernetes.io/name=argocd-image-updater', 'ArgoCD Image Updater'),
        }

        results = {}

        for key, (namespace, selector, display_name) in components.items():
            pods = self.k8s.get_pods(namespace, selector)
            running = any(p.get('status', {}).get('phase') == 'Running' for p in pods)

            if running:
                self.print_success(f"{display_name} is running")
                results[key] = True
                self.add_result(f"component_{key}", True, f"{display_name} running")
            else:
                self.print_warning(f"{display_name} not found (may not be enabled)")
                results[key] = False
                self.add_result(f"component_{key}", False, f"{display_name} not running")

        print()
        return results

    def verify_storage_addons(self) -> Dict[str, bool]:
        """Step 7: Check storage add-ons"""
        self.print_header("Step 7: Check Storage Add-ons")

        storage = {
            'ebs_csi': ('kube-system', 'app=ebs-csi-controller', 'EBS CSI Driver'),
            'efs_csi': ('kube-system', 'app=efs-csi-controller', 'EFS CSI Driver'),
        }

        results = {}

        for key, (namespace, selector, display_name) in storage.items():
            pods = self.k8s.get_pods(namespace, selector)
            running = any(p.get('status', {}).get('phase') == 'Running' for p in pods)

            if running:
                self.print_success(f"{display_name} is running")
                results[key] = True
            else:
                self.print_warning(f"{display_name} not found")
                results[key] = False

        print()
        return results

    def get_argocd_credentials(self) -> Optional[str]:
        """Step 8: Get ArgoCD admin credentials"""
        self.print_header("Step 8: ArgoCD Access Information")

        password = self.k8s.get_secret('argocd-initial-admin-secret', 'argocd', 'password')

        if password:
            self.print_info("ArgoCD Admin Credentials:")
            print(f"  Username: admin")
            print(f"  Password: {password}")
            print()
            self.print_info("Access ArgoCD UI:")
            print(f"  kubectl port-forward svc/argocd-server -n argocd 8080:443")
            print(f"  Then visit: https://localhost:8080")
            self.add_result("argocd_credentials", True, "Credentials retrieved")
            return password
        else:
            self.print_warning("ArgoCD admin secret not found")
            self.add_result("argocd_credentials", False, "Credentials not found")
            return None

    def calculate_health_score(self) -> Tuple[int, HealthStatus]:
        """Calculate overall health score"""
        passed = len([r for r in self.results if r.passed])
        total = len(self.results)

        if total == 0:
            return 0, HealthStatus.CRITICAL

        percentage = int((passed / total) * 100)

        if percentage >= 90:
            status = HealthStatus.EXCELLENT
        elif percentage >= 70:
            status = HealthStatus.GOOD
        elif percentage >= 50:
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.CRITICAL

        return percentage, status

    def print_summary(self):
        """Print verification summary"""
        self.print_header("Deployment Verification Summary")

        health_score, health_status = self.calculate_health_score()
        passed = len([r for r in self.results if r.passed])
        total = len(self.results)

        # Print health score with color coding
        if health_status == HealthStatus.EXCELLENT:
            self.print_success(f"Platform Health: {health_score}% ({passed}/{total} checks passed)")
            self.print_success("Deployment verification PASSED")
        elif health_status == HealthStatus.GOOD:
            self.print_success(f"Platform Health: {health_score}% ({passed}/{total} checks passed)")
            self.print_info("Some components may still be initializing")
        elif health_status == HealthStatus.DEGRADED:
            self.print_warning(f"Platform Health: {health_score}% ({passed}/{total} checks passed)")
            self.print_warning("Significant issues detected - review required")
        else:
            self.print_error(f"Platform Health: {health_score}% ({passed}/{total} checks passed)")
            self.print_error("Deployment may have issues - review logs above")

        print()
        self.print_info("For detailed application status:")
        print("  kubectl get applications -n argocd")
        print()
        self.print_info("To watch application sync progress:")
        print("  watch kubectl get applications -n argocd")
        print()

        return health_score

    def run(self) -> int:
        """Run full verification"""
        self.print_banner()

        # Step 1: Configure kubectl
        if not self.verify_kubectl_config():
            return 1

        # Step 2: Verify connectivity
        if not self.verify_cluster_connectivity():
            return 1

        # Step 3: Check nodes
        self.verify_nodes()

        # Step 4: Check ArgoCD
        self.verify_argocd()

        # Step 5: Check applications
        self.verify_applications()

        # Step 6: Check platform components
        self.verify_platform_components()

        # Step 7: Check storage
        self.verify_storage_addons()

        # Step 8: Get credentials
        self.get_argocd_credentials()

        # Summary
        health_score = self.print_summary()

        # Exit code based on health
        return 0 if health_score >= 70 else 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Verify EKS single-build deployment health',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scripts/verify_deployment.py --cluster goldenpath-dev-eks --region us-east-1
  python3 scripts/verify_deployment.py -c my-cluster -r eu-west-2

Exit Codes:
  0: Verification successful (health >= 70%)
  1: Verification failed or critical error
        """
    )

    parser.add_argument(
        '--cluster', '-c',
        required=True,
        help='EKS cluster name'
    )

    parser.add_argument(
        '--region', '-r',
        required=True,
        help='AWS region'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )

    args = parser.parse_args()

    verifier = DeploymentVerifier(args.cluster, args.region)

    try:
        exit_code = verifier.run()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Color.YELLOW}Verification interrupted by user{Color.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Color.RED}Error during verification: {e}{Color.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
