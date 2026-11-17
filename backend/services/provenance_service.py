import json
from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.database.models import ProvenanceRecord, Job, DatasetVersion, Dataset

class ProvenanceService:
    @staticmethod
    def create_lineage(
        db: Session,
        tenant_id: str,
        job_id: str,
        dataset_version_id: str,
        engine_name: str,
        tool_version: str,
        reference_db_version: str,
        s3_output_uri: str,
        evidence_type: str = "validated_algorithmic"
    ) -> Dict[str, Any]:
        """
        Builds W3C PROV-O graph representation and stores in database.
        """
        now = datetime.now(timezone.utc).isoformat()
        job = db.query(Job).filter(Job.id == job_id).first()
        ds_ver = db.query(DatasetVersion).filter(DatasetVersion.id == dataset_version_id).first()
        dataset = db.query(Dataset).filter(Dataset.id == ds_ver.dataset_id).first() if ds_ver else None

        provenance_id = job.provenance_id if job else f"prov-{job_id}"

        lineage_graph = {
            "w3c_prov": {
                "entity": {
                    "dataset:raw": {
                        "prov:id": dataset.id if dataset else "unknown-dataset",
                        "prov:label": dataset.name if dataset else "Raw Dataset",
                        "s3_uri": dataset.s3_uri if dataset else None
                    },
                    "dataset:version": {
                        "prov:id": ds_ver.id if ds_ver else "unknown-version",
                        "sha256": ds_ver.sha256_hash if ds_ver else None,
                        "sequence_count": ds_ver.sequence_count if ds_ver else 0,
                        "total_bp": ds_ver.total_bp if ds_ver else 0
                    },
                    "reference_db:target": {
                        "version": reference_db_version,
                        "prov:label": "Target Reference DB"
                    },
                    "artifact:results_parquet": {
                        "s3_output_uri": s3_output_uri,
                        "format": "Apache Parquet"
                    }
                },
                "activity": {
                    "activity:analysis_run": {
                        "job_id": job_id,
                        "engine": engine_name,
                        "tool_version": tool_version,
                        "started_at": job.created_at.isoformat() if job and job.created_at else now,
                        "completed_at": now
                    }
                },
                "agent": {
                    "agent:gisap_worker": {
                        "prov:type": "prov:SoftwareAgent",
                        "name": "GISAP Nextflow Engine",
                        "tenant_id": tenant_id
                    }
                },
                "wasGeneratedBy": {
                    "artifact:results_parquet": "activity:analysis_run"
                },
                "used": [
                    {"activity": "activity:analysis_run", "entity": "dataset:version"},
                    {"activity": "activity:analysis_run", "entity": "reference_db:target"}
                ],
                "wasDerivedFrom": {
                    "dataset:version": "dataset:raw"
                }
            },
            "metadata": {
                "provenance_id": provenance_id,
                "tenant_id": tenant_id,
                "evidence_type": evidence_type,
                "timestamp": now
            }
        }

        record = ProvenanceRecord(
            tenant_id=tenant_id,
            job_id=job_id,
            entity_type="analysis_artifact",
            entity_id=s3_output_uri,
            engine_name=engine_name,
            tool_version=tool_version,
            reference_db_version=reference_db_version,
            evidence_type=evidence_type,
            lineage_json=json.dumps(lineage_graph)
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        return lineage_graph

    @staticmethod
    def get_job_provenance(db: Session, tenant_id: str, job_id: str) -> Dict[str, Any]:
        record = db.query(ProvenanceRecord).filter(
            ProvenanceRecord.tenant_id == tenant_id,
            ProvenanceRecord.job_id == job_id
        ).order_by(ProvenanceRecord.created_at.desc()).first()

        if record:
            return json.loads(record.lineage_json)

        # Fallback empty lineage
        return {
            "provenance_id": f"prov-{job_id}",
            "tenant_id": tenant_id,
            "status": "pending_or_not_found"
        }
