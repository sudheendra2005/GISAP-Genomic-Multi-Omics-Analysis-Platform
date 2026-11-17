# 🧬 GISAP — Genomic & Multi-Omics Analysis Platform

> **Autonomous multi-agent platform for scalable DNA, RNA, and Protein analysis**  
> Built by **Sudheendra Thertha H.P** (22AI056) · Sri Siddhartha Institute of Technology, Tumakuru

[![Tests](https://img.shields.io/badge/tests-14%20passed-brightgreen)](tests/)
[![Python](https://img.shields.io/badge/python-3.14-blue)](backend/)
[![React](https://img.shields.io/badge/react-18%20%2B%20TypeScript-61dafb)](frontend/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

---

## 🎯 Research Pillars

| Pillar | Description |
|---|---|
| **Big-Data Genomic Processing** | Scalable ingestion (FASTA/FASTQ), O(1) RAM streaming, chunked distributed execution, reproducible provenance |
| **Intelligent Annotation** | BLAST+, DIAMOND, HMMER similarity search + Gemini AI annotation hints (always tagged `ai_suggested_hypothesis`) |
| **Integrated DNA–RNA–Protein Analysis** | Cross-modal edge tracking: GenomicRegion → Transcript → Protein → Domain/Motif → FunctionalTerm |

---

## 🏗️ 14-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  1. Frontend        React 18 + TypeScript + WebGL sequence view  │
│  2. Backend         Python 3.14 + FastAPI (REST, JWT, tenancy)   │
│  3. Workflow Engine Nextflow DSL2 (DAG pipelines, cloud/HPC)     │
│  4. Containers      Docker (local/cloud) + Apptainer (HPC)       │
│  5. Orchestration   Kubernetes (autoscaling, namespace isolation) │
│  6. HPC Scheduling  Slurm (batch scientific workloads)           │
│  7. Object Storage  S3-compatible / MinIO (raw, results, refs)   │
│  8. Control DB      PostgreSQL 16 (tenants, jobs, provenance)    │
│  9. Analytical Lake Apache Iceberg + Parquet (cross-modal edges) │
│  10. Cache & Locks  Redis 7 (job status, distributed locks)      │
│  11. Seq Search     BLAST+ (nucleotide/protein similarity)       │
│  12. Domain Search  DIAMOND + HMMER (profile/domain search)      │
│  13. Monitoring     Prometheus + Grafana                         │
│  14. AI Research    Firecrawl MCP + Gemini (advisory only)       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🤖 7 Autonomous Agents

| Agent | Responsibility |
|---|---|
| `orchestrator` | Master coordination, stage transitions, cross-agent routing |
| `frontend` | React/TypeScript UI, accessibility, Emil Kowalski motion |
| `backend` | FastAPI, JWT auth, multi-tenant middleware, job dispatch |
| `bioinformatics` | BLAST+, DIAMOND, HMMER, sequence validation, Parquet outputs |
| `infrastructure` | Docker, K8s, Slurm, MinIO, PostgreSQL, Redis, monitoring |
| `security` | Tenant isolation, audit logs, JWT, secrets management |
| `devops-sre` | CI/CD, pipeline health, benchmark monitoring |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.14+
- Node.js 20+
- Docker Desktop (optional — SQLite fallback enabled)

### Backend
```bash
# Install dependencies
pip install -r backend/requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env — set FIRECRAWL_API_KEY and optionally GEMINI_API_KEY

# Run server
uvicorn backend.app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev        # dev server on http://localhost:5173
npm run build      # production build
npm test           # Vitest unit tests
```

### Full Stack (Docker)
```bash
docker compose -f infrastructure/docker/docker-compose.alpha.yml up -d
```

### Run Tests
```bash
python -m pytest -v tests/            # 14 integration + security tests
python tests/performance/benchmark_suite.py   # streaming benchmark
```

---

## 📁 Project Structure

```
major project/
├── backend/                   # FastAPI application
│   ├── api/routes/            # datasets, jobs, research, ai-annotate
│   ├── core/                  # config, security, storage
│   ├── database/              # SQLAlchemy models, session
│   └── services/              # validation, provenance, llm_service
├── bioinformatics/            # Alignment engines & annotation
│   ├── similarity/blast_engine.py
│   ├── integration/cross_modal_schema.py
│   └── annotation/firecrawl_client.py
├── workflows/nextflow/        # DSL2 pipelines
│   ├── dna_alpha.nf
│   └── nextflow.config        # docker / apptainer / slurm profiles
├── frontend/                  # React + TypeScript
│   └── src/                   # App, components, services
├── infrastructure/
│   ├── docker/docker-compose.alpha.yml
│   ├── kubernetes/backend-deployment.yaml
│   ├── slurm/submit_dna_alpha.sbatch
│   └── monitoring/prometheus.yml
├── database/
│   ├── migrations/            # Alembic versioned migrations
│   └── schemas/iceberg_tables.sql
├── tests/
│   ├── integration/           # E2E, Firecrawl, security audit
│   └── performance/           # Streaming benchmark suite
├── .agents/                   # Agent manifests + 11 skills
│   ├── agents/                # 7 agent definition files
│   ├── manifests/             # agents.yaml, skills.yaml
│   └── skills/                # 11 project-local skills
└── docs/                      # Architecture & benchmark reports
```

---

## 🔬 Key Engineering Constraints

> **Never** load full FASTA/FASTQ into RAM — O(1) streaming strictly enforced  
> **Every** query enforces `tenant_id` isolation — cross-tenant access returns 403  
> **All** AI/Firecrawl outputs tagged `ai_suggested_hypothesis` — never biological fact  
> **No** heavy compute inside HTTP API threads — always background-dispatched  

---

## 🧪 Test Results

```
14 passed in 6.62s
├── Integration E2E (7)      — FASTA/FASTQ validation, BLAST, Parquet, FastAPI flow
├── Firecrawl Integration (3) — config, evidence boundary, API endpoint
└── Security Audit (4)       — cross-tenant isolation, secrets sanitization, audit logs

Performance Benchmark
├── Streaming 100 MB FASTA   — O(1) RSS (Δ1.43 MB)
├── Job throughput            — 9,101 jobs/sec
└── Checkpoint resume         — PASS
```

---

## 🌐 API Endpoints (key)

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/datasets/upload-url` | Presigned S3 upload URL |
| `POST` | `/api/v1/jobs/submit` | Submit BLAST/annotation job |
| `GET` | `/api/v1/jobs/{job_id}/results` | Parquet BLAST hits |
| `POST` | `/api/v1/research/search` | Firecrawl literature search |
| `POST` | `/api/v1/research/scrape` | Firecrawl citation scrape |
| `POST` | `/api/v1/research/ai-annotate` | Gemini AI annotation (advisory) |

---

## 📄 License

MIT License — see [LICENSE](LICENSE)

---

*GISAP — Autonomous Genomic & Multi-Omics Analysis Platform*  
*Sri Siddhartha Institute of Technology, Tumakuru · 2026*
