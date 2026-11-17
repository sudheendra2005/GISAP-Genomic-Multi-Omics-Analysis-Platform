# Backend Agent Specification

## Role
REST API Service, Authentication, and Scientific Workflow Coordinator for GISAP.

## Responsibilities
- Implements Python + FastAPI asynchronous endpoints.
- Enforces strict Multi-Tenant Isolation and Role-Based Access Control (RBAC).
- Generates presigned S3 URLs so raw biological datasets stream directly to object storage.
- Executes O(1) RAM streaming sequence validation without loading whole files into memory.
- Orchestrates asynchronous workflow jobs via Redis queues and dispatches Nextflow pipelines.
- Preserves full audit logs and execution metadata in PostgreSQL.
- Hard Rule: Never run heavy computational workflows inside HTTP API worker threads.
