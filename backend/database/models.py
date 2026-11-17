import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Integer,
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    Index
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="tenant", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(64), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(32), nullable=False, default="analyst")  # admin, bioinformatician, analyst, viewer
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    tenant = relationship("Tenant", back_populates="users")


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(64), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    tenant = relationship("Tenant", back_populates="projects")
    datasets = relationship("Dataset", back_populates="project", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="project", cascade="all, delete-orphan")


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(64), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(String(64), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    sequence_type = Column(String(32), nullable=False)  # dna, rna, protein
    format = Column(String(32), nullable=False)         # fasta, fastq
    s3_uri = Column(String(512), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    project = relationship("Project", back_populates="datasets")
    versions = relationship("DatasetVersion", back_populates="dataset", cascade="all, delete-orphan")


class DatasetVersion(Base):
    __tablename__ = "dataset_versions"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(64), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    dataset_id = Column(String(64), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False, default=1)
    sha256_hash = Column(String(64), nullable=False, index=True)
    sequence_count = Column(Integer, nullable=False, default=0)
    total_bp = Column(BigInteger, nullable=False, default=0)
    s3_uri = Column(String(512), nullable=False)
    is_valid = Column(Boolean, nullable=False, default=False)
    validation_errors = Column(Text, nullable=True)  # JSON-encoded errors if any
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    dataset = relationship("Dataset", back_populates="versions")

    __table_args__ = (
        Index("ix_dataset_version_tenant_hash", "tenant_id", "sha256_hash"),
    )


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(64), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(String(64), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    dataset_version_id = Column(String(64), ForeignKey("dataset_versions.id", ondelete="SET NULL"), nullable=True, index=True)
    job_type = Column(String(64), nullable=False)  # blast, diamond, hmmer, dna_alpha
    status = Column(String(32), nullable=False, default="pending")  # pending, running, completed, failed
    params = Column(Text, nullable=True)           # JSON-encoded parameters
    s3_output_uri = Column(String(512), nullable=True)
    provenance_id = Column(String(64), nullable=False, index=True, default=generate_uuid)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    project = relationship("Project", back_populates="jobs")
    provenance_records = relationship("ProvenanceRecord", back_populates="job", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_job_tenant_status", "tenant_id", "status"),
    )


class ProvenanceRecord(Base):
    __tablename__ = "provenance_records"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(64), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(String(64), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_type = Column(String(64), nullable=False)  # sequence, hit, domain, edge
    entity_id = Column(String(128), nullable=False)
    engine_name = Column(String(64), nullable=False)
    tool_version = Column(String(64), nullable=False)
    reference_db_version = Column(String(64), nullable=False)
    evidence_type = Column(String(64), nullable=False)  # validated_algorithmic, ai_suggested_hypothesis
    lineage_json = Column(Text, nullable=False)        # JSON serialized W3C PROV graph
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    job = relationship("Job", back_populates="provenance_records")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(64), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(64), nullable=True)
    action = Column(String(64), nullable=False)        # CREATE, UPDATE, DELETE, EXECUTE, ACCESS
    resource_type = Column(String(64), nullable=False) # dataset, job, result, tenant
    resource_id = Column(String(64), nullable=False)
    details = Column(Text, nullable=True)              # JSON sanitized details
    ip_address = Column(String(45), nullable=True)
    timestamp = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    __table_args__ = (
        Index("ix_audit_tenant_time", "tenant_id", "timestamp"),
    )
