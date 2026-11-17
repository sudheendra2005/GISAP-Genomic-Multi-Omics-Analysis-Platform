import io
import os
import json
import tempfile
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.services.validation_service import SequenceValidationService
from bioinformatics.similarity.blast_engine import BlastEngine
from bioinformatics.integration.cross_modal_schema import (
    write_blast_hits_parquet,
    read_blast_hits_parquet,
    write_cross_modal_edges,
    read_cross_modal_edges,
    CROSS_MODAL_EDGE_SCHEMA
)

client = TestClient(app)

SAMPLE_FASTA = b"""\
>seq1 E. coli K12 fragment
AGCTTTTCATTCTGACTGCAACGGGCAATATGTCTCTGTGTGGATTAAAAAAAGAGTGTCTGATAGCAGC
>seq2 S. cerevisiae fragment
CCACACCACACCCACACACCCACACACCACACCACACCCACACACCCACACACCACACCCACACACCACA
"""

SAMPLE_FASTQ = b"""\
@SEQ_ID_001
AGCTTTTCATTCTGACTGCAACGGGCAATATGTCTCTGTGTGGATTAAAAAAAGAGTGTCTGATAGCAGC
+
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
@SEQ_ID_002
CCACACCACACCCACACACCCACACACCACACCACACCCACACACCCACACACCACACCCACACACCACA
+
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
"""

def test_streaming_validation_fasta():
    stream = io.BytesIO(SAMPLE_FASTA)
    result = SequenceValidationService.validate_stream(stream, format_type="fasta", sequence_type="dna")
    assert result["is_valid"] is True
    assert result["sequence_count"] == 2
    assert result["total_bp"] == 140
    assert len(result["sha256"]) == 64
    assert len(result["errors"]) == 0

def test_streaming_validation_fastq():
    stream = io.BytesIO(SAMPLE_FASTQ)
    result = SequenceValidationService.validate_stream(stream, format_type="fastq", sequence_type="dna")
    assert result["is_valid"] is True
    assert result["sequence_count"] == 2
    assert result["total_bp"] == 140
    assert len(result["errors"]) == 0

def test_streaming_validation_invalid():
    bad_data = b">bad_seq\nAGCTXYZ123\n"
    stream = io.BytesIO(bad_data)
    result = SequenceValidationService.validate_stream(stream, format_type="fasta", sequence_type="dna")
    assert result["is_valid"] is False
    assert len(result["errors"]) > 0

def test_blast_similarity_engine():
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".fasta") as q_file, \
         tempfile.NamedTemporaryFile("w", delete=False, suffix=".fasta") as db_file:
        q_file.write(">q1\nAGCTTTTCATTCTGACTGCAACGGGCAATATGTCTCTGTG\n")
        q_file.flush()
        db_file.write(">db1\nAGCTTTTCATTCTGACTGCAACGGGCAATATGTCTCTGTGTGGATTAAAAAAAGAGTGTCTGATAGCAGC\n")
        db_file.flush()

        q_path = q_file.name
        db_path = db_file.name

    try:
        hits = BlastEngine.run_blastn(q_path, db_path)
        assert len(hits) > 0
        hit = hits[0]
        assert hit["qseqid"] == "q1"
        assert hit["sseqid"] == "db1"
        assert hit["pident"] == 100.0
        assert hit["length"] == 40
        assert hit["bitscore"] > 0
    finally:
        if os.path.exists(q_path): os.remove(q_path)
        if os.path.exists(db_path): os.remove(db_path)

def test_parquet_serialization_roundtrip():
    hits = [{
        "qseqid": "q1",
        "sseqid": "s1",
        "pident": 99.5,
        "length": 100,
        "mismatch": 1,
        "gapopen": 0,
        "qstart": 1,
        "qend": 100,
        "sstart": 10,
        "send": 110,
        "evalue": 1e-45,
        "bitscore": 185.2
    }]
    with tempfile.NamedTemporaryFile(delete=False, suffix=".parquet") as tmp:
        tmp_path = tmp.name

    try:
        write_blast_hits_parquet(hits, "prov-test-123", "ssit-tumakuru", tmp_path)
        recovered = read_blast_hits_parquet(tmp_path)
        assert len(recovered) == 1
        assert recovered[0]["qseqid"] == "q1"
        assert recovered[0]["pident"] == 99.5
        assert recovered[0]["provenance_id"] == "prov-test-123"
        assert recovered[0]["tenant_id"] == "ssit-tumakuru"
    finally:
        if os.path.exists(tmp_path): os.remove(tmp_path)

def test_cross_modal_edge_schema():
    edges = [{
        "edge_id": "edge-001",
        "source_type": "Transcript",
        "source_id": "ENST00000380152",
        "relationship": "TRANSLATED_TO",
        "target_type": "Protein",
        "target_id": "ENSP00000369497",
        "attributes_json": json.dumps({"frame": 1}),
        "provenance_id": "prov-alpha-001",
        "tenant_id": "ssit-tumakuru",
        "engine_name": "GISAP_Translation_Engine",
        "tool_version": "1.0.0",
        "reference_db_version": "GENCODE_v44",
        "confidence_score": 1.0,
        "evidence_type": "validated_algorithmic",
        "created_at": "2026-11-18T00:00:00Z"
    }]
    with tempfile.NamedTemporaryFile(delete=False, suffix=".parquet") as tmp:
        tmp_path = tmp.name

    try:
        write_cross_modal_edges(edges, tmp_path)
        recovered = read_cross_modal_edges(tmp_path)
        assert len(recovered) == 1
        assert recovered[0]["relationship"] == "TRANSLATED_TO"
        assert recovered[0]["evidence_type"] == "validated_algorithmic"
    finally:
        if os.path.exists(tmp_path): os.remove(tmp_path)

def test_fastapi_alpha_e2e_flow():
    tenant_header = {"X-Tenant-ID": "ssit-tumakuru"}

    # 1. System Health
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "online"

    # 2. Dataset Presign
    presign_req = {
        "project_id": "proj-alpha-01",
        "name": "EColi_K12_Sample",
        "sequence_type": "dna",
        "format": "fasta",
        "filename": "ecoli_sample.fasta"
    }
    res = client.post("/api/v1/datasets/presign", json=presign_req, headers=tenant_header)
    assert res.status_code == 200
    presign_data = res.json()
    dataset_id = presign_data["dataset_id"]
    assert "s3_uri" in presign_data

    # 3. Direct upload to local storage fallback
    s3_parts = presign_data["s3_uri"].replace("s3://", "").split("/", 1)
    bucket, key = s3_parts
    upload_res = client.post(
        f"/api/v1/datasets/upload-direct?bucket={bucket}&key={key}",
        files={"file": ("ecoli_sample.fasta", SAMPLE_FASTA, "text/plain")}
    )
    assert upload_res.status_code == 200

    # 4. Dataset Validation (O(1) Streaming)
    val_res = client.post(f"/api/v1/datasets/{dataset_id}/validate", headers=tenant_header)
    assert val_res.status_code == 200
    val_data = val_res.json()
    assert val_data["is_valid"] is True
    assert val_data["sequence_count"] == 2
    version_id = val_data["version_id"]

    # 5. Submit Analysis Job
    job_req = {
        "project_id": "proj-alpha-01",
        "dataset_version_id": version_id,
        "job_type": "dna_alpha",
        "params": {"evalue": 10.0},
        "reference_db": "ncbi_refseq_core_v1"
    }
    job_res = client.post("/api/v1/jobs", json=job_req, headers=tenant_header)
    assert job_res.status_code == 202
    job_id = job_res.json()["job_id"]

    # 6. Retrieve Job Status
    status_res = client.get(f"/api/v1/jobs/{job_id}", headers=tenant_header)
    assert status_res.status_code == 200

    # 7. Retrieve Job Results
    results_res = client.get(f"/api/v1/jobs/{job_id}/results", headers=tenant_header)
    assert results_res.status_code == 200

    # 8. Retrieve Full Provenance Lineage
    prov_res = client.get(f"/api/v1/jobs/{job_id}/provenance", headers=tenant_header)
    assert prov_res.status_code == 200
    prov_data = prov_res.json()
    assert "w3c_prov" in prov_data or "provenance_id" in prov_data
