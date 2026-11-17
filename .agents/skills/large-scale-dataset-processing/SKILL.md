---
name: large-scale-dataset-processing
description: Petabyte-scale dataset partitioning, scatter-gather chunking, and S3 streaming.
---

# Large-Scale Dataset Processing

## Overview
Scales analysis from gigabytes to terabytes/petabytes using scatter-gather chunking and partition indexing.

## Patterns
- Stream byte ranges directly from S3 using HTTP Range headers.
- Partition analytical tables by `(tenant_id, organism, dataset_version)`.
- Enforce O(1) resident set size (RSS) memory ceiling for worker nodes.
- Maintain idempotent resume tokens for long-running batch jobs.
