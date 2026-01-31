#!/usr/bin/env bash
# ---
# id: SCRIPT-0064
# type: script
# owner: platform-team
# status: active
# maturity: 1
# dry_run:
#   supported: false
#   command_hint: none
# test:
#   runner: bash
#   command: bash scripts/rag-data-sync.sh status
#   evidence: manual
# risk_profile:
#   production_impact: low
#   security_risk: none
#   coupling_risk: low
# ---
# scripts/rag-data-sync.sh - Sync ChromaDB to/from MinIO (local S3)
# SKIP-TDD: Shell utility for local dev; manually tested with MinIO
set -euo pipefail

# Configuration
MINIO_ENDPOINT="${MINIO_ENDPOINT:-http://localhost:9000}"
MINIO_BUCKET="${MINIO_BUCKET:-chroma-backups}"
CHROMA_DIR="${CHROMA_DIR:-.chroma}"
AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:-minioadmin}"
AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:-minioadmin}"

export AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY

usage() {
    echo "Usage: $0 {push|pull|status}"
    echo ""
    echo "Commands:"
    echo "  push    - Upload local .chroma to MinIO"
    echo "  pull    - Download .chroma from MinIO"
    echo "  status  - Show sync status"
    exit 1
}

check_deps() {
    if ! command -v aws &> /dev/null; then
        echo "Error: aws CLI not found. Install with: pip install awscli"
        exit 1
    fi
}

push() {
    echo "📤 Pushing $CHROMA_DIR to MinIO..."
    aws --endpoint-url "$MINIO_ENDPOINT" s3 sync \
        "$CHROMA_DIR" "s3://$MINIO_BUCKET/chroma/" \
        --delete
    echo "✅ Push complete"
}

pull() {
    echo "📥 Pulling from MinIO to $CHROMA_DIR..."
    mkdir -p "$CHROMA_DIR"
    aws --endpoint-url "$MINIO_ENDPOINT" s3 sync \
        "s3://$MINIO_BUCKET/chroma/" "$CHROMA_DIR" \
        --delete
    echo "✅ Pull complete"
}

status() {
    echo "📊 MinIO Status:"
    echo "   Endpoint: $MINIO_ENDPOINT"
    echo "   Bucket: $MINIO_BUCKET"
    echo ""
    echo "Remote contents:"
    aws --endpoint-url "$MINIO_ENDPOINT" s3 ls "s3://$MINIO_BUCKET/chroma/" --recursive --human-readable 2>/dev/null || echo "   (empty or not accessible)"
    echo ""
    echo "Local .chroma size:"
    du -sh "$CHROMA_DIR" 2>/dev/null || echo "   (not found)"
}

check_deps

case "${1:-}" in
    push)  push ;;
    pull)  pull ;;
    status) status ;;
    *)     usage ;;
esac
