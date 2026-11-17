---
name: fasta-fastq-processing
description: Process and chunk FASTA and FASTQ biological sequences in O(1) memory streams.
---

# FASTA & FASTQ Stream Processing

## Overview
Processes massive biological sequence files from S3 streams or chunked readers without loading complete files into memory.

## Guidelines
- Read FASTA headers (`>header`) and multiline sequences incrementally.
- Read FASTQ 4-line records (Identifier, Sequence, Separator, Quality scores) sequentially.
- Calculate base frequencies (A, C, G, T/U, N) and GC content iteratively.
- Stream chunks directly to downstream processors or temporary scratch storage.
