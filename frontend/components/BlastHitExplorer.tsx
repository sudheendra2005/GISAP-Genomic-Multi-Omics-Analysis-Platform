import React, { useEffect, useState } from 'react';
import { Search, ExternalLink, Dna } from 'lucide-react';
import { apiService } from '../services/api';

interface BlastHitExplorerProps {
  tenantId: string;
  jobId: string | null;
}

export const BlastHitExplorer: React.FC<BlastHitExplorerProps> = ({ tenantId, jobId }) => {
  const [hits, setHits] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!jobId) return;
    setLoading(true);
    apiService.getJobResults(jobId, tenantId)
      .then((res) => setHits(res.hits || []))
      .catch(() => setHits([]))
      .finally(() => setLoading(false));
  }, [jobId, tenantId]);

  if (!jobId) return null;

  return (
    <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.5rem', marginBottom: '1.5rem' }}>
      <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#f8fafc', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Dna color="#34d399" size={22} />
        BLAST Similarity Hit Explorer (Structured Parquet Records)
      </h2>

      {loading ? (
        <div style={{ padding: '2rem', textAlign: 'center', color: '#94a3b8' }}>Loading analytical hits from S3...</div>
      ) : hits.length === 0 ? (
        <div style={{ padding: '1.5rem', textAlign: 'center', color: '#94a3b8' }}>No hits detected above E-value threshold.</div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #475569', color: '#94a3b8' }}>
                <th style={{ padding: '0.75rem 0.5rem' }}>Query ID</th>
                <th style={{ padding: '0.75rem 0.5rem' }}>Subject Accession</th>
                <th style={{ padding: '0.75rem 0.5rem' }}>Identity %</th>
                <th style={{ padding: '0.75rem 0.5rem' }}>Alignment Length</th>
                <th style={{ padding: '0.75rem 0.5rem' }}>Query Span</th>
                <th style={{ padding: '0.75rem 0.5rem' }}>Subject Span</th>
                <th style={{ padding: '0.75rem 0.5rem' }}>Bit Score</th>
                <th style={{ padding: '0.75rem 0.5rem' }}>E-Value</th>
              </tr>
            </thead>
            <tbody>
              {hits.map((h, i) => (
                <tr key={i} style={{ borderBottom: '1px solid #334155', color: '#f1f5f9' }}>
                  <td style={{ padding: '0.75rem 0.5rem', fontWeight: 500, color: '#38bdf8' }}>{h.qseqid}</td>
                  <td style={{ padding: '0.75rem 0.5rem', fontWeight: 500, color: '#a78bfa' }}>{h.sseqid}</td>
                  <td style={{ padding: '0.75rem 0.5rem' }}>
                    <span style={{ padding: '0.2rem 0.5rem', borderRadius: '4px', background: h.pident >= 90 ? 'rgba(34, 197, 94, 0.2)' : 'rgba(234, 179, 8, 0.2)', color: h.pident >= 90 ? '#4ade80' : '#facc15' }}>
                      {h.pident.toFixed(1)}%
                    </span>
                  </td>
                  <td style={{ padding: '0.75rem 0.5rem' }}>{h.length} bp</td>
                  <td style={{ padding: '0.75rem 0.5rem' }}>{h.qstart}..{h.qend}</td>
                  <td style={{ padding: '0.75rem 0.5rem' }}>{h.sstart}..{h.send}</td>
                  <td style={{ padding: '0.75rem 0.5rem', fontWeight: 600 }}>{h.bitscore}</td>
                  <td style={{ padding: '0.75rem 0.5rem', fontFamily: 'monospace' }}>{h.evalue.toExponential(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
