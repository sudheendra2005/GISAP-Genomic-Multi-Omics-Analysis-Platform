---
name: sequence-validation
description: Streaming sequence integrity, IUPAC validation, and SHA-256 fingerprinting.
---

# Sequence Validation & Checksumming

## Overview
Validates sequence structure, alphabet conformance (IUPAC nucleotide or amino acid codes), quality score boundaries (Phred 33/64), and calculates cryptographic SHA-256 digests in streaming O(1) memory.

## Rules
- Reject invalid characters or malformed record delimiters immediately.
- Compute SHA-256 checksum over the raw byte stream as chunks are read.
- Record sequence count, total base pairs, and error metrics for dataset versioning.
