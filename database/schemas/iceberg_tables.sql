-- GISAP Cross-Modal Apache Iceberg Table Definitions
-- Partitioning scheme: (tenant_id, organism, dataset_version)

-- 1. GenomicRegion (DNA)
CREATE TABLE IF NOT EXISTS gisap_catalog.bioinformatics.genomic_region (
    region_id STRING,
    chromosome STRING,
    start_pos BIGINT,
    end_pos BIGINT,
    strand STRING,
    gc_content DOUBLE,
    provenance_id STRING,
    tenant_id STRING,
    engine_name STRING,
    tool_version STRING,
    reference_db_version STRING,
    confidence_score DOUBLE,
    evidence_type STRING, -- 'validated_algorithmic' vs 'ai_suggested_hypothesis'
    created_at TIMESTAMP
)
USING iceberg
PARTITIONED BY (tenant_id, reference_db_version);

-- 2. Transcript (RNA)
CREATE TABLE IF NOT EXISTS gisap_catalog.bioinformatics.transcript (
    transcript_id STRING,
    gene_id STRING,
    biotype STRING,
    exon_count INT,
    length_bp BIGINT,
    provenance_id STRING,
    tenant_id STRING,
    engine_name STRING,
    tool_version STRING,
    reference_db_version STRING,
    confidence_score DOUBLE,
    evidence_type STRING,
    created_at TIMESTAMP
)
USING iceberg
PARTITIONED BY (tenant_id);

-- 3. Protein
CREATE TABLE IF NOT EXISTS gisap_catalog.bioinformatics.protein (
    protein_id STRING,
    transcript_id STRING,
    amino_acid_length INT,
    molecular_weight_da DOUBLE,
    isoelectric_point DOUBLE,
    provenance_id STRING,
    tenant_id STRING,
    engine_name STRING,
    tool_version STRING,
    reference_db_version STRING,
    confidence_score DOUBLE,
    evidence_type STRING,
    created_at TIMESTAMP
)
USING iceberg
PARTITIONED BY (tenant_id);

-- 4. DomainOrMotif (HMMER)
CREATE TABLE IF NOT EXISTS gisap_catalog.bioinformatics.domain_or_motif (
    domain_id STRING,
    accession STRING,
    domain_name STRING,
    evalue DOUBLE,
    bitscore DOUBLE,
    provenance_id STRING,
    tenant_id STRING,
    engine_name STRING,
    tool_version STRING,
    reference_db_version STRING,
    confidence_score DOUBLE,
    evidence_type STRING,
    created_at TIMESTAMP
)
USING iceberg
PARTITIONED BY (tenant_id);

-- 5. FunctionalTerm
CREATE TABLE IF NOT EXISTS gisap_catalog.bioinformatics.functional_term (
    term_id STRING,
    ontology STRING, -- 'GO', 'KEGG', 'Pfam'
    name STRING,
    definition STRING,
    provenance_id STRING,
    tenant_id STRING,
    engine_name STRING,
    tool_version STRING,
    reference_db_version STRING,
    confidence_score DOUBLE,
    evidence_type STRING,
    created_at TIMESTAMP
)
USING iceberg
PARTITIONED BY (tenant_id, ontology);

-- 6. CrossModalEdge
CREATE TABLE IF NOT EXISTS gisap_catalog.bioinformatics.cross_modal_edge (
    edge_id STRING,
    source_type STRING,
    source_id STRING,
    relationship STRING, -- 'TRANSCRIBED_FROM', 'TRANSLATED_TO', 'HAS_SIMILARITY', 'CONTAINS_DOMAIN', 'ASSOCIATED_WITH'
    target_type STRING,
    target_id STRING,
    attributes_json STRING,
    provenance_id STRING,
    tenant_id STRING,
    engine_name STRING,
    tool_version STRING,
    reference_db_version STRING,
    confidence_score DOUBLE,
    evidence_type STRING,
    created_at TIMESTAMP
)
USING iceberg
PARTITIONED BY (tenant_id, relationship);
