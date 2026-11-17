import React, { useEffect, useState } from 'react';
import { GitBranch, ShieldCheck, Database, Cpu } from 'lucide-react';
import { apiService } from '../services/api';

interface ProvenanceViewerProps {
  tenantId: string;
  jobId: string | null;
}

export const ProvenanceViewer: React.FC<ProvenanceViewerProps> = ({ tenantId, jobId }) => {
  const [provenance, setProvenance] = useState<any>(null);

  useEffect(() => {
    if (!jobId) return;
    apiService.getJobProvenance(jobId, tenantId)
      .then((data) => setProvenance(data))
      .catch(() => setProvenance(null));
  }, [jobId, tenantId]);

  if (!jobId || !provenance) return null;

  const entities = provenance.w3c_prov?.entity || {};
  const activities = provenance.w3c_prov?.activity || {};

  return (
    <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.5rem', marginBottom: '1.5rem' }}>
      <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#f8fafc', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <GitBranch color="#f472b6" size={22} />
        W3C PROV-O Biological Lineage & Audit Trail
      </h2>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', alignItems: 'center', justifyContent: 'space-between', padding: '1rem', background: '#0f172a', borderRadius: '8px', border: '1px solid #334155' }}>
        {/* Node 1: Raw Input */}
        <div style={{ flex: '1 1 200px', padding: '0.75rem', background: '#1e293b', borderRadius: '6px', borderLeft: '4px solid #38bdf8' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#94a3b8', fontSize: '0.75rem', textTransform: 'uppercase' }}>
            <Database size={14} /> Input Dataset
          </div>
          <div style={{ fontWeight: 600, color: '#f8fafc', marginTop: '0.2rem' }}>{entities['dataset:raw']?.['prov:label'] || 'Raw Sequences'}</div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.2rem' }}>
            SHA: <code>{entities['dataset:version']?.sha256?.substring(0, 10)}...</code>
          </div>
        </div>

        <span style={{ color: '#475569', fontSize: '1.5rem' }}>&rarr;</span>

        {/* Node 2: Activity */}
        <div style={{ flex: '1 1 200px', padding: '0.75rem', background: '#1e293b', borderRadius: '6px', borderLeft: '4px solid #a78bfa' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#94a3b8', fontSize: '0.75rem', textTransform: 'uppercase' }}>
            <Cpu size={14} /> Scientific Activity
          </div>
          <div style={{ fontWeight: 600, color: '#f8fafc', marginTop: '0.2rem' }}>{activities['activity:analysis_run']?.engine || 'BLAST+ Nextflow'}</div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.2rem' }}>
            Ref: {entities['reference_db:target']?.version || 'NCBI RefSeq'}
          </div>
        </div>

        <span style={{ color: '#475569', fontSize: '1.5rem' }}>&rarr;</span>

        {/* Node 3: Result Artifact */}
        <div style={{ flex: '1 1 200px', padding: '0.75rem', background: '#1e293b', borderRadius: '6px', borderLeft: '4px solid #34d399' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#94a3b8', fontSize: '0.75rem', textTransform: 'uppercase' }}>
            <ShieldCheck size={14} /> Analytical Artifact
          </div>
          <div style={{ fontWeight: 600, color: '#f8fafc', marginTop: '0.2rem' }}>Apache Parquet / Iceberg</div>
          <div style={{ fontSize: '0.75rem', color: '#34d399', marginTop: '0.2rem' }}>
            Type: {provenance.metadata?.evidence_type || 'validated_algorithmic'}
          </div>
        </div>
      </div>

      <div style={{ marginTop: '1rem', padding: '0.75rem', background: '#0f172a', borderRadius: '6px', fontSize: '0.8rem', color: '#cbd5e1' }}>
        <strong>Immutable Lineage Identifier:</strong> <code style={{ color: '#f472b6' }}>{provenance.metadata?.provenance_id}</code>
      </div>
    </div>
  );
};
