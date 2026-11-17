---
name: protein-domain-analysis
description: Protein domain identification and profile HMM analysis using HMMER and DIAMOND.
---

# Protein Domain Analysis

## Overview
Discovers conserved domains, active sites, and profile matches across protein translations using HMMER (`hmmscan`/`hmmsearch`) and DIAMOND.

## Guidelines
- Extract envelope coordinates, E-values, and model scores.
- Link identified domains into the cross-modal knowledge schema as `DomainOrMotif` entities.
- Store relations via `CONTAINS_DOMAIN` edges connecting Protein to Domain.
