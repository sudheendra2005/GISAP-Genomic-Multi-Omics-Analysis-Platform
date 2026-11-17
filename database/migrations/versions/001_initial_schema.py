"""001_initial_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-11-18 01:40:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Tenants
    op.create_table(
        "tenants",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # 2. Users
    op.create_table(
        "users",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("tenant_id", sa.String(64), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_tenant_id", "users", ["tenant_id"])

    # 3. Projects
    op.create_table(
        "projects",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("tenant_id", sa.String(64), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_projects_tenant_id", "projects", ["tenant_id"])

    # 4. Datasets
    op.create_table(
        "datasets",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("tenant_id", sa.String(64), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("project_id", sa.String(64), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("sequence_type", sa.String(32), nullable=False),
        sa.Column("format", sa.String(32), nullable=False),
        sa.Column("s3_uri", sa.String(512), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_datasets_tenant_id", "datasets", ["tenant_id"])
    op.create_index("ix_datasets_project_id", "datasets", ["project_id"])

    # 5. Dataset Versions
    op.create_table(
        "dataset_versions",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("tenant_id", sa.String(64), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("dataset_id", sa.String(64), sa.ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("sha256_hash", sa.String(64), nullable=False),
        sa.Column("sequence_count", sa.Integer(), nullable=False),
        sa.Column("total_bp", sa.BigInteger(), nullable=False),
        sa.Column("s3_uri", sa.String(512), nullable=False),
        sa.Column("is_valid", sa.Boolean(), nullable=False),
        sa.Column("validation_errors", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_dataset_versions_tenant_id", "dataset_versions", ["tenant_id"])
    op.create_index("ix_dataset_versions_dataset_id", "dataset_versions", ["dataset_id"])
    op.create_index("ix_dataset_versions_sha256_hash", "dataset_versions", ["sha256_hash"])
    op.create_index("ix_dataset_version_tenant_hash", "dataset_versions", ["tenant_id", "sha256_hash"])

    # 6. Jobs
    op.create_table(
        "jobs",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("tenant_id", sa.String(64), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("project_id", sa.String(64), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("dataset_version_id", sa.String(64), sa.ForeignKey("dataset_versions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("job_type", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("params", sa.Text(), nullable=True),
        sa.Column("s3_output_uri", sa.String(512), nullable=True),
        sa.Column("provenance_id", sa.String(64), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_jobs_tenant_id", "jobs", ["tenant_id"])
    op.create_index("ix_jobs_provenance_id", "jobs", ["provenance_id"])
    op.create_index("ix_job_tenant_status", "jobs", ["tenant_id", "status"])

    # 7. Provenance Records
    op.create_table(
        "provenance_records",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("tenant_id", sa.String(64), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("job_id", sa.String(64), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("entity_type", sa.String(64), nullable=False),
        sa.Column("entity_id", sa.String(128), nullable=False),
        sa.Column("engine_name", sa.String(64), nullable=False),
        sa.Column("tool_version", sa.String(64), nullable=False),
        sa.Column("reference_db_version", sa.String(64), nullable=False),
        sa.Column("evidence_type", sa.String(64), nullable=False),
        sa.Column("lineage_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_provenance_records_tenant_id", "provenance_records", ["tenant_id"])
    op.create_index("ix_provenance_records_job_id", "provenance_records", ["job_id"])

    # 8. Audit Logs
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("tenant_id", sa.String(64), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(64), nullable=True),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("resource_type", sa.String(64), nullable=False),
        sa.Column("resource_id", sa.String(64), nullable=False),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_audit_logs_tenant_id", "audit_logs", ["tenant_id"])
    op.create_index("ix_audit_tenant_time", "audit_logs", ["tenant_id", "timestamp"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("provenance_records")
    op.drop_table("jobs")
    op.drop_table("dataset_versions")
    op.drop_table("datasets")
    op.drop_table("projects")
    op.drop_table("users")
    op.drop_table("tenants")
