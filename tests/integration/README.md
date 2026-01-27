# Integration Tests

**Purpose:** Tier 3 tests that validate component interactions and end-to-end workflows.

> "Integration tests are selective — use them for workflows that cross boundaries."
> — GOV-0017

---

## When to Use Integration Tests

Use integration tests when:
- Multiple scripts work together in sequence
- External services are involved (mocked or real)
- State persists across operations

| Workflow | Components | Test Focus |
|----------|------------|------------|
| ECR Sync | parser → pusher → registry | Image lands in ECR |
| Secret Flow | request → parser → AWS SDK | Secret created in SSM |
| RDS Provision | request → parser → psql | Database exists |

---

## Directory Structure

```
tests/integration/
├── README.md                      # This file
├── conftest.py                    # Integration fixtures (mocks, cleanup)
├── test_ecr_sync_workflow.py      # ECR sync end-to-end
├── test_secret_provisioning.py    # Secret creation flow
└── fixtures/
    ├── mock_responses/
    │   └── ecr_describe_images.json
    └── test_data/
        └── sample-image.tar
```

---

## Writing an Integration Test

```python
import pytest
from unittest.mock import patch, MagicMock

class TestECRSyncWorkflow:
    """Integration tests for ECR sync workflow."""

    @pytest.fixture
    def mock_ecr_client(self):
        """Mock boto3 ECR client."""
        with patch("boto3.client") as mock:
            client = MagicMock()
            mock.return_value = client
            yield client

    def test_sync_pushes_new_image(self, mock_ecr_client, tmp_path):
        """New image should be pushed to ECR."""
        from scripts.ecr_sync import sync_images

        # Setup
        mock_ecr_client.describe_images.return_value = {"imageDetails": []}

        # Execute
        result = sync_images(
            source="local",
            target="aws",
            image="backstage:latest"
        )

        # Verify
        assert result.pushed == 1
        mock_ecr_client.put_image.assert_called_once()

    def test_sync_skips_existing_image(self, mock_ecr_client):
        """Existing image should be skipped."""
        from scripts.ecr_sync import sync_images

        # Setup - image already exists
        mock_ecr_client.describe_images.return_value = {
            "imageDetails": [{"imageDigest": "sha256:abc123"}]
        }

        # Execute
        result = sync_images(
            source="local",
            target="aws",
            image="backstage:latest"
        )

        # Verify
        assert result.pushed == 0
        assert result.skipped == 1
```

---

## Integration Test Patterns

### 1. Mock External Services
```python
@pytest.fixture
def mock_aws(mocker):
    """Mock AWS services for testing."""
    return {
        "ecr": mocker.patch("boto3.client")("ecr"),
        "ssm": mocker.patch("boto3.client")("ssm"),
    }
```

### 2. Cleanup After Test
```python
@pytest.fixture
def temp_resource(request):
    """Create temporary resource, cleanup after test."""
    resource = create_resource()
    yield resource
    # Cleanup
    delete_resource(resource.id)
```

### 3. Test Data Isolation
```python
@pytest.fixture
def isolated_namespace():
    """Use unique namespace per test to avoid collisions."""
    import uuid
    return f"test-{uuid.uuid4().hex[:8]}"
```

---

## CI Enforcement

Integration tests run:
- On PRs touching critical paths (when `integration` label is added)
- Nightly scheduled run
- Before production promotions

**Note:** Integration tests are slower and may require credentials. They are **not** required for every PR.

---

## Related

- [GOV-0017: TDD and Determinism](../../docs/10-governance/policies/GOV-0017-tdd-and-determinism.md)
- [tests/contract/](../contract/) — Contract tests (faster, no external deps)
