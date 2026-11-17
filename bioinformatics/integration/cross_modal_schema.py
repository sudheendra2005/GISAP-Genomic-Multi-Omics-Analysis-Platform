import pyarrow as pa
import pyarrow.parquet as pq
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any

# Common Metadata Fields on every Node and Edge
METADATA_FIELDS = [
    pa.field("provenance_id", pa.string(), nullable=False),
    pa.field("tenant_id", pa.string(), nullable=False),
    pa.field("engine_name", pa.string(), nullable=False),
    pa.field("tool_version", pa.string(), nullable=False),
    pa.field("reference_db_version", pa.string(), nullable=False),
    pa.field("confidence_score", pa.float64(), nullable=False),
    pa.field("evidence_type", pa.string(), nullable=False),  # validated_algorithmic vs ai_suggested_hypothesis
    pa.field("created_at", pa.string(), nullable=False),
]

# 1. GenomicRegion (DNA)
GENOMIC_REGION_SCHEMA = pa.schema([
    pa.field("region_id", pa.string(), nullable=False),
    pa.field("chromosome", pa.string(), nullable=False),
    pa.field("start_pos", pa.int64(), nullable=False),
    pa.field("end_pos", pa.int64(), nullable=False),
    pa.field("strand", pa.string(), nullable=False),
    pa.field("gc_content", pa.float64(), nullable=True),
] + METADATA_FIELDS)

# 2. Transcript (RNA)
TRANSCRIPT_SCHEMA = pa.schema([
    pa.field("transcript_id", pa.string(), nullable=False),
    pa.field("gene_id", pa.string(), nullable=False),
    pa.field("biotype", pa.string(), nullable=False),
    pa.field("exon_count", pa.int32(), nullable=False),
    pa.field("length_bp", pa.int64(), nullable=False),
] + METADATA_FIELDS)

# 3. Protein
PROTEIN_SCHEMA = pa.schema([
    pa.field("protein_id", pa.string(), nullable=False),
    pa.field("transcript_id", pa.string(), nullable=False),
    pa.field("amino_acid_length", pa.int32(), nullable=False),
    pa.field("molecular_weight_da", pa.float64(), nullable=True),
    pa.field("isoelectric_point", pa.float64(), nullable=True),
] + METADATA_FIELDS)

# 4. DomainOrMotif (HMMER)
DOMAIN_OR_MOTIF_SCHEMA = pa.schema([
    pa.field("domain_id", pa.string(), nullable=False),
    pa.field("accession", pa.string(), nullable=False),
    pa.field("domain_name", pa.string(), nullable=False),
    pa.field("evalue", pa.float64(), nullable=False),
    pa.field("bitscore", pa.float64(), nullable=False),
] + METADATA_FIELDS)

# 5. FunctionalTerm (GO, KEGG)
FUNCTIONAL_TERM_SCHEMA = pa.schema([
    pa.field("term_id", pa.string(), nullable=False),
    pa.field("ontology", pa.string(), nullable=False),  # GO, KEGG, Pfam
    pa.field("name", pa.string(), nullable=False),
    pa.field("definition", pa.string(), nullable=True),
] + METADATA_FIELDS)

# 6. CrossModalEdge
CROSS_MODAL_EDGE_SCHEMA = pa.schema([
    pa.field("edge_id", pa.string(), nullable=False),
    pa.field("source_type", pa.string(), nullable=False), # GenomicRegion, Transcript, Protein, DomainOrMotif, FunctionalTerm
    pa.field("source_id", pa.string(), nullable=False),
    pa.field("relationship", pa.string(), nullable=False), # TRANSCRIBED_FROM, TRANSLATED_TO, HAS_SIMILARITY, CONTAINS_DOMAIN, ASSOCIATED_WITH
    pa.field("target_type", pa.string(), nullable=False),
    pa.field("target_id", pa.string(), nullable=False),
    pa.field("attributes_json", pa.string(), nullable=True),
] + METADATA_FIELDS)

# BLAST Hits Parquet Schema
BLAST_HITS_SCHEMA = pa.schema([
    pa.field("qseqid", pa.string(), nullable=False),
    pa.field("sseqid", pa.string(), nullable=False),
    pa.field("pident", pa.float64(), nullable=False),
    pa.field("length", pa.int32(), nullable=False),
    pa.field("mismatch", pa.int32(), nullable=False),
    pa.field("gapopen", pa.int32(), nullable=False),
    pa.field("qstart", pa.int32(), nullable=False),
    pa.field("qend", pa.int32(), nullable=False),
    pa.field("sstart", pa.int32(), nullable=False),
    pa.field("send", pa.int32(), nullable=False),
    pa.field("evalue", pa.float64(), nullable=False),
    pa.field("bitscore", pa.float64(), nullable=False),
    pa.field("provenance_id", pa.string(), nullable=False),
    pa.field("tenant_id", pa.string(), nullable=False),
])

def write_blast_hits_parquet(hits: List[Dict[str, Any]], provenance_id: str, tenant_id: str, output_path: str):
    data = {
        "qseqid": [h["qseqid"] for h in hits],
        "sseqid": [h["sseqid"] for h in hits],
        "pident": [float(h["pident"]) for h in hits],
        "length": [int(h["length"]) for h in hits],
        "mismatch": [int(h["mismatch"]) for h in hits],
        "gapopen": [int(h["gapopen"]) for h in hits],
        "qstart": [int(h["qstart"]) for h in hits],
        "qend": [int(h["qend"]) for h in hits],
        "sstart": [int(h["sstart"]) for h in hits],
        "send": [int(h["send"]) for h in hits],
        "evalue": [float(h["evalue"]) for h in hits],
        "bitscore": [float(h["bitscore"]) for h in hits],
        "provenance_id": [provenance_id] * len(hits),
        "tenant_id": [tenant_id] * len(hits),
    }
    table = pa.Table.from_pydict(data, schema=BLAST_HITS_SCHEMA)
    pq.write_table(table, output_path, compression="snappy")
    return output_path

def read_blast_hits_parquet(parquet_path: str) -> List[Dict[str, Any]]:
    table = pq.read_table(parquet_path)
    return table.to_pylist()

def write_cross_modal_edges(edges: List[Dict[str, Any]], output_path: str):
    data = {f.name: [e.get(f.name) for e in edges] for f in CROSS_MODAL_EDGE_SCHEMA}
    table = pa.Table.from_pydict(data, schema=CROSS_MODAL_EDGE_SCHEMA)
    pq.write_table(table, output_path, compression="snappy")
    return output_path

def read_cross_modal_edges(parquet_path: str) -> List[Dict[str, Any]]:
    table = pq.read_table(parquet_path)
    return table.to_pylist()
