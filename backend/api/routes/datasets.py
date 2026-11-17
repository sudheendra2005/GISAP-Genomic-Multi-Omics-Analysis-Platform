import os
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.api.deps import get_db, get_tenant_id, get_current_user, require_role
from backend.core.config import settings
from backend.core.storage import storage_manager
from backend.database.models import Dataset, DatasetVersion, Project, AuditLog
from backend.services.validation_service import SequenceValidationService

router = APIRouter(prefix="/datasets", tags=["Datasets"])

class PresignRequest(BaseModel):
    project_id: str
    name: str
    sequence_type: str = Field(default="dna", description="dna, rna, or protein")
    format: str = Field(default="fasta", description="fasta or fastq")
    filename: str

class PresignResponse(BaseModel):
    dataset_id: str
    upload_url: str
    method: str
    s3_uri: str
    storage_tier: str

class ValidationResponse(BaseModel):
    dataset_id: str
    version_id: str
    version_number: int
    is_valid: bool
    sha256_hash: str
    sequence_count: int
    total_bp: int
    errors: list

@router.post("/presign", response_model=PresignResponse)
def get_presigned_upload_url(
    req: PresignRequest,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(require_role(["admin", "bioinformatician", "analyst"])),
    db: Session = Depends(get_db)
):
    # Verify or create project under tenant
    project = db.query(Project).filter(Project.id == req.project_id, Project.tenant_id == tenant_id).first()
    if not project:
        project = Project(id=req.project_id, tenant_id=tenant_id, name="Default Project")
        db.add(project)
        db.commit()

    dataset_id = str(uuid.uuid4())
    s3_key = f"{tenant_id}/{project.id}/{dataset_id}/{req.filename}"

    presign_info = storage_manager.generate_presigned_upload_url(
        bucket=settings.S3_BUCKET_RAW,
        key=s3_key
    )

    dataset = Dataset(
        id=dataset_id,
        tenant_id=tenant_id,
        project_id=project.id,
        name=req.name,
        sequence_type=req.sequence_type.lower(),
        format=req.format.lower(),
        s3_uri=presign_info["s3_uri"]
    )
    db.add(dataset)

    # Log audit
    audit = AuditLog(
        tenant_id=tenant_id,
        user_id=current_user.get("sub"),
        action="CREATE",
        resource_type="dataset",
        resource_id=dataset_id,
        details=f"Presigned URL requested for {req.name}"
    )
    db.add(audit)
    db.commit()

    return PresignResponse(
        dataset_id=dataset_id,
        upload_url=presign_info["upload_url"],
        method=presign_info["method"],
        s3_uri=presign_info["s3_uri"],
        storage_tier=presign_info["storage_tier"]
    )

@router.post("/{id}/validate", response_model=ValidationResponse)
def validate_dataset(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(require_role(["admin", "bioinformatician", "analyst"])),
    db: Session = Depends(get_db)
):
    dataset = db.query(Dataset).filter(Dataset.id == id, Dataset.tenant_id == tenant_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found or access denied")

    # Extract bucket and key from s3_uri (s3://bucket/key)
    s3_parts = dataset.s3_uri.replace("s3://", "").split("/", 1)
    if len(s3_parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid S3 URI stored on dataset")

    bucket, key = s3_parts

    try:
        stream = storage_manager.get_stream(bucket, key)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Raw biological file not yet uploaded to S3")

    # Stream validate in O(1) RAM
    try:
        val_result = SequenceValidationService.validate_stream(
            stream=stream,
            format_type=dataset.format,
            sequence_type=dataset.sequence_type
        )
    finally:
        if hasattr(stream, "close"):
            stream.close()

    # Determine version number
    prev_ver = db.query(DatasetVersion).filter(
        DatasetVersion.dataset_id == id,
        DatasetVersion.tenant_id == tenant_id
    ).order_by(DatasetVersion.version_number.desc()).first()

    next_ver_num = (prev_ver.version_number + 1) if prev_ver else 1
    version_id = str(uuid.uuid4())

    new_version = DatasetVersion(
        id=version_id,
        tenant_id=tenant_id,
        dataset_id=id,
        version_number=next_ver_num,
        sha256_hash=val_result["sha256"],
        sequence_count=val_result["sequence_count"],
        total_bp=val_result["total_bp"],
        s3_uri=dataset.s3_uri,
        is_valid=val_result["is_valid"],
        validation_errors="; ".join(val_result["errors"]) if val_result["errors"] else None
    )
    db.add(new_version)

    # Audit log
    audit = AuditLog(
        tenant_id=tenant_id,
        user_id=current_user.get("sub"),
        action="EXECUTE",
        resource_type="dataset_version",
        resource_id=version_id,
        details=f"Validation completed. Valid={val_result['is_valid']}, SHA={val_result['sha256'][:8]}"
    )
    db.add(audit)
    db.commit()

    return ValidationResponse(
        dataset_id=id,
        version_id=version_id,
        version_number=next_ver_num,
        is_valid=val_result["is_valid"],
        sha256_hash=val_result["sha256"],
        sequence_count=val_result["sequence_count"],
        total_bp=val_result["total_bp"],
        errors=val_result["errors"]
    )

@router.post("/upload-direct")
async def upload_direct_file(
    bucket: str = Query(...),
    key: str = Query(...),
    file: UploadFile = File(...)
):
    """Local fallback direct upload endpoint when MinIO is in standby."""
    contents = await file.read()
    storage_manager.put_bytes(bucket, key, contents)
    return {"status": "uploaded", "s3_uri": f"s3://{bucket}/{key}", "bytes": len(contents)}
