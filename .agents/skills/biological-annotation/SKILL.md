---
name: biological-annotation
description: Evidence-based functional and taxonomic annotation with strict confidence tracking.
---

# Biological Annotation

## Overview
Maps sequence alignment and profile hits to biological ontology terms (GO, KEGG, Pfam, RefSeq).

## Rules
- Every annotation record must reference source evidence (`provenance_id`, `tool_version`, `reference_db_version`).
- Mark all AI-derived inferences as `ai_suggested_hypothesis`.
- Mark all direct deterministic alignments as `validated_algorithmic`.
- Never fabricate reference alignments or confidence scores.
