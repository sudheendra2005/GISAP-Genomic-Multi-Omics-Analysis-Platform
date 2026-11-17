---
name: nextflow-development
description: Nextflow DSL2 scientific pipeline development with multi-profile support.
---

# Nextflow Development

## Overview
Designs reproducible, container-isolated scientific workflow pipelines using Nextflow DSL2.

## Requirements
- Define modular processes with explicit `input`, `output`, and `script` blocks.
- Support execution profiles: `docker` (local/cloud containers), `apptainer` (HPC), and `slurm` (batch scheduler).
- Enable checkpointing and pipeline resumption via `-resume`.
- Stream intermediate files directly to/from S3-compatible object storage.
