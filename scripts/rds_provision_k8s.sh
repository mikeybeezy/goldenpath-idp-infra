#!/bin/bash
# RDS Provisioning via K8s Job
# Runs rds_provision.py from inside the cluster where it can reach private RDS
set -euo pipefail

ENV="${1:-dev}"
REGION="${2:-eu-west-2}"
REPO="${3:-mikeybeezy/goldenpath-idp-infra}"

echo "Running RDS provisioning from inside the cluster..."

if ! kubectl cluster-info >/dev/null 2>&1; then
    echo "ERROR: Cannot connect to Kubernetes cluster."
    echo "Run: aws eks update-kubeconfig --name <cluster> --region $REGION"
    exit 1
fi

JOB_NAME="rds-provision-${ENV}-$(date +%s)"
NAMESPACE="external-secrets"
SERVICE_ACCOUNT="external-secrets"

echo "Creating K8s Job: $JOB_NAME"
echo "Namespace: $NAMESPACE (using ESO service account for Secrets Manager access)"

kubectl apply -f - <<EOFYAML
apiVersion: batch/v1
kind: Job
metadata:
  name: $JOB_NAME
  namespace: $NAMESPACE
  labels:
    app: rds-provisioning
    environment: $ENV
spec:
  ttlSecondsAfterFinished: 300
  backoffLimit: 1
  template:
    metadata:
      labels:
        app: rds-provisioning
    spec:
      serviceAccountName: $SERVICE_ACCOUNT
      restartPolicy: Never
      containers:
        - name: provisioner
          image: python:3.11-slim
          command:
            - /bin/bash
            - -c
            - |
              set -e
              echo "Installing dependencies..."
              apt-get update && apt-get install -y git >/dev/null 2>&1
              pip install boto3 psycopg2-binary pyyaml >/dev/null 2>&1
              echo "Cloning repository..."
              git clone --depth=1 https://github.com/$REPO.git /workspace
              cd /workspace
              echo "Running provisioning..."
              python3 scripts/rds_provision.py \\
                --env $ENV \\
                --tfvars envs/${ENV}-rds/terraform.tfvars \\
                --master-secret goldenpath/${ENV}/rds/master \\
                --build-id k8s-job \\
                --run-id $JOB_NAME \\
                --region $REGION
          env:
            - name: AWS_REGION
              value: $REGION
            - name: AWS_DEFAULT_REGION
              value: $REGION
EOFYAML

echo "Waiting for job $JOB_NAME to complete (timeout: 5m)..."
echo ""

# Heartbeat loop with status checking
TIMEOUT=300
ELAPSED=0
INTERVAL=5
SPINNER=('⠋' '⠙' '⠹' '⠸' '⠼' '⠴' '⠦' '⠧' '⠇' '⠏')
SPIN_IDX=0

while [ $ELAPSED -lt $TIMEOUT ]; do
    # Check job status
    STATUS=$(kubectl get job/$JOB_NAME -n $NAMESPACE -o jsonpath='{.status.conditions[?(@.type=="Complete")].status}' 2>/dev/null || echo "")
    FAILED=$(kubectl get job/$JOB_NAME -n $NAMESPACE -o jsonpath='{.status.conditions[?(@.type=="Failed")].status}' 2>/dev/null || echo "")

    if [ "$STATUS" == "True" ]; then
        echo -e "\r✅ Job completed successfully after ${ELAPSED}s                    "
        echo ""
        echo "=== Job Logs ==="
        kubectl logs job/$JOB_NAME -n $NAMESPACE
        exit 0
    fi

    if [ "$FAILED" == "True" ]; then
        echo -e "\r❌ Job failed after ${ELAPSED}s                    "
        echo ""
        echo "=== Job Logs ==="
        kubectl logs job/$JOB_NAME -n $NAMESPACE 2>/dev/null || true
        echo ""
        echo "=== Job Events ==="
        kubectl describe job/$JOB_NAME -n $NAMESPACE | tail -20
        exit 1
    fi

    # Get pod phase for more detail
    POD_PHASE=$(kubectl get pods -n $NAMESPACE -l job-name=$JOB_NAME -o jsonpath='{.items[0].status.phase}' 2>/dev/null || echo "Pending")

    # Print heartbeat with spinner
    printf "\r${SPINNER[$SPIN_IDX]} Waiting... [%3ds/%ds] Pod: %-12s" "$ELAPSED" "$TIMEOUT" "$POD_PHASE"
    SPIN_IDX=$(( (SPIN_IDX + 1) % ${#SPINNER[@]} ))

    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
done

# Timeout reached
echo -e "\r⏱️  Job timed out after ${TIMEOUT}s                    "
echo ""
echo "=== Job Logs ==="
kubectl logs job/$JOB_NAME -n $NAMESPACE 2>/dev/null || true
echo ""
echo "=== Job Events ==="
kubectl describe job/$JOB_NAME -n $NAMESPACE | tail -20
exit 1
