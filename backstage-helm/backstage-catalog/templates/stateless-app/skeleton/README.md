# ${{ values.component_id }}

${{ values.description }}

This service uses the **Stateless App Golden Path**.

## Development

1.  Create virtual env: `python -m venv venv && source venv/bin/activate`
2.  Install dependencies: `pip install -r requirements.txt`
3.  Run locally: `python app.py`

## Deployment

Deployment is handled by the Platform CI/CD:
*   **Push to main**: Triggers Docker build + ECR push + ArgoCD sync.
*   **Live URL**: `https://${{ values.component_id }}.${{ values.environment }}.goldenpathidp.io` (approx)

## Governance

*   **Owner**: ${{ values.owner }}
*   **System**: goldenpath-idp
