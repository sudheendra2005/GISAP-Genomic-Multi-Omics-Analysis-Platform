---
name: provenance-management
description: End-to-end W3C PROV-O biological lineage and audit graph management.
---

# Provenance Management

## Overview
Captures and serializes the complete scientific lineage of every analytical artifact in the GISAP platform.

## Lineage Chain
`Original Dataset` -> `Dataset Version (SHA-256)` -> `Analysis Config` -> `Workflow Version` -> `Reference DB Version` -> `Execution Environment` -> `Output Parquet Artifacts`.

## Metadata Keys
- `provenance_id`: Unique UUIDv4 lineage identifier.
- `tenant_id`: Partition ownership identifier.
- `tool_version`: Exact binary/container version.
- `reference_db_version`: Reference release identifier.
- `evidence_type`: `validated_algorithmic` vs. `ai_suggested_hypothesis`.
- `created_at`: ISO 8601 UTC timestamp.
