# GISAP — Autonomous Multi-Agent Governance & Stack Architecture

## 1. Project Identity & Research Pillars
GISAP (Genomic & Multi-Omics Analysis Platform) processes, analyzes, annotates, and integrates biological datasets across DNA, RNA, and Protein domains.
- **Pillar 1: Big-Data Genomic Processing**: Scalable ingestion (FASTA/FASTQ), chunking, distributed execution, and reproducible provenance. Raw biological datasets must remain in S3-compatible object storage and NEVER be loaded entirely into RAM.
- **Pillar 2: Intelligent Annotation**: Sequence identification, similarity searches, and evidence-based functional annotation. Strict boundary: AI-assisted annotation must NEVER fabricate evidence or alignments.
- **Pillar 3: Integrated DNA–RNA–Protein Analysis**: Cross-modal relationship tracking linking GenomicRegion -> Transcript -> Protein -> Domain/Motif -> FunctionalTerm with auditable provenance.

## 2. Approved 14-Layer Technical Architecture
1. **Frontend**: React + TypeScript (Accessible UI, purposeful motion, WebGL/Canvas sequence view, provenance lineage graph).
2. **Backend**: Python + FastAPI (REST APIs, AuthN/AuthZ, tenant isolation, S3 presigned URL generation, job lifecycle).
3. **Workflow Engine**: Nextflow (DAG pipelines, containerized task isolation, cloud/HPC portability).
4. **Containerization**: Docker (Local/Cloud) + Apptainer (HPC).
5. **Cloud Orchestration**: Kubernetes (Scalable container orchestration, autoscaling).
6. **HPC Scheduling**: Slurm (Cluster scientific batch scheduling).
7. **Object Storage**: S3-compatible storage / MinIO (`raw-sequences`, `intermediates`, `results`, `reference-dbs`).
8. **Control Metadata**: PostgreSQL 16 (Tenants, users, projects, datasets, dataset_versions, jobs, provenance_records, audit_logs).
9. **Analytical Data Lake**: Apache Iceberg + Parquet (Partitioned analytical schemas, cross-modal edges).
10. **Caching & Locks**: Redis 7 (Job status caching, queue coordination, distributed locks).
11. **Sequence Search**: BLAST+ (Modular nucleotide and protein similarity).
12. **Protein/Domain Search**: DIAMOND + HMMER (Profile and domain search).
13. **Monitoring**: Prometheus + Grafana (Host/worker metrics, S3 I/O, job throughput, failure rates).
14. **Agent Research Integration**: Firecrawl MCP (External documentation & literature search; citations preserved; strictly advisory).

## 3. Mandatory Engineering Constraints
- Never run heavy computational workflows inside HTTP API processes.
- Never load entire FASTA/FASTQ files into memory; validate via O(1) RAM streaming chunks.
- Every dataset, job, and result record must enforce `tenant_id` isolation.
- Every analysis output must preserve full provenance lineage (Dataset Version -> Workflow Version -> Reference DB Version -> Output Artifacts).
- External skills & research tools (Firecrawl, Emil Kowalski UI) must maintain clean boundaries and never be tangled into core scientific compute.
