---
name: blast-workflows
description: Modular BLAST+ execution pipelines for nucleotide and protein similarity.
---

# BLAST Workflows

## Overview
Executes BLAST searches (blastn, blastp, blastx) against indexed reference databases using containerized or modular engines.

## Guidelines
- Parse tabular `-outfmt 6` or JSON outputs into structured records (qseqid, sseqid, pident, length, mismatch, gapopen, qstart, qend, sstart, send, evalue, bitscore).
- Persist structured hits directly to Parquet tables in object storage.
- Attach complete database version and algorithm parameter metadata to every run.
