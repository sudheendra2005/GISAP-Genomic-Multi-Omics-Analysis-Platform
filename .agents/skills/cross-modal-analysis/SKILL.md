---
name: cross-modal-analysis
description: Multi-omics cross-modal integration linking DNA, RNA, and Protein domains into Iceberg tables.
---

# Cross-Modal Multi-Omics Analysis

## Overview
Connects heterogeneous biological entities into an integrated knowledge graph stored across partitioned Apache Iceberg and Parquet tables.

## Entity & Edge Model
- Entities:
  - `GenomicRegion` (DNA coordinates, chromosome, start, end, strand)
  - `Transcript` (RNA transcript ID, splice structure, expression)
  - `Protein` (UniProt ID, amino acid sequence, molecular weight)
  - `DomainOrMotif` (Pfam/CDD domain, coordinates, score)
  - `FunctionalTerm` (GO term, KEGG pathway, description)
- Relationships (Edges):
  - `TRANSCRIBED_FROM`: RNA -> DNA
  - `TRANSLATED_TO`: RNA -> Protein
  - `HAS_SIMILARITY`: Entity -> Entity (BLAST/DIAMOND hit)
  - `CONTAINS_DOMAIN`: Protein -> DomainOrMotif (HMMER profile match)
  - `ASSOCIATED_WITH`: Entity -> FunctionalTerm
