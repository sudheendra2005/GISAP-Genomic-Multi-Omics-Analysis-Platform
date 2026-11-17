import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.core.config import settings
from backend.database.session import SessionLocal
from backend.database.models import AuditLog

client = TestClient(app)

def test_cross_tenant_dataset_access_blocked():
    # 1. Create dataset under Tenant Alpha
    alpha_header = {"X-Tenant-ID": "tenant-alpha"}
    presign_req = {
        "project_id": "proj-alpha",
        "name": "Confidential_Genomic_Alpha.fasta",
        "sequence_type": "dna",
        "format": "fasta",
        "filename": "alpha.fasta"
    }
    res = client.post("/api/v1/datasets/presign", json=presign_req, headers=alpha_header)
    assert res.status_code == 200
    dataset_id = res.json()["dataset_id"]

    # 2. Attempt access from Tenant Beta
    beta_header = {"X-Tenant-ID": "tenant-beta"}
    validate_res = client.post(f"/api/v1/datasets/{dataset_id}/validate", headers=beta_header)
    assert validate_res.status_code in (403, 404), "Cross-tenant access must be rejected with 403 or 404"

def test_cross_tenant_job_results_blocked():
    alpha_header = {"X-Tenant-ID": "tenant-alpha"}
    beta_header = {"X-Tenant-ID": "tenant-beta"}

    # Attempt to query non-existent or foreign job from tenant beta
    res = client.get("/api/v1/jobs/non-existent-or-foreign-job-id", headers=beta_header)
    assert res.status_code == 404

def test_secrets_sanitization():
    # Verify health endpoint never exposes secrets
    res = client.get("/health")
    assert res.status_code == 200
    body_text = res.text.lower()
    assert settings.JWT_SECRET.lower() not in body_text
    assert settings.S3_SECRET_KEY.lower() not in body_text
    assert "password" not in body_text

def test_audit_logs_record_mutations():
    tenant_id = "tenant-audit-test"
    header = {"X-Tenant-ID": tenant_id}

    presign_req = {
        "project_id": "proj-audit",
        "name": "Audit_Sample.fasta",
        "sequence_type": "dna",
        "format": "fasta",
        "filename": "audit.fasta"
    }
    res = client.post("/api/v1/datasets/presign", json=presign_req, headers=header)
    assert res.status_code == 200

    # Query DB to verify audit_logs table has mutation record
    db = SessionLocal()
    try:
        logs = db.query(AuditLog).filter(AuditLog.tenant_id == tenant_id).all()
        assert len(logs) > 0
        actions = [l.action for l in logs]
        assert "CREATE" in actions
    finally:
        db.close()
