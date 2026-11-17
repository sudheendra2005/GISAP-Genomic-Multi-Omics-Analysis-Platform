import React, { useState } from 'react';
import { Play, Settings2 } from 'lucide-react';
import { apiService } from '../services/api';

interface JobSubmissionProps {
  tenantId: string;
  datasetVersionId: string | null;
  onJobSubmitted: (jobId: string) => void;
}

export const JobSubmission: React.FC<JobSubmissionProps> = ({ tenantId, datasetVersionId, onJobSubmitted }) => {
  const [jobType, setJobType] = useState('dna_alpha');
  const [evalue, setEvalue] = useState('10.0');
  const [refDb, setRefDb] = useState('ncbi_refseq_core_v1');
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = async () => {
    if (!datasetVersionId) return;
    setSubmitting(true);
    setErrorMsg('');

    try {
      const res = await apiService.submitJob({
        project_id: 'default-project',
        dataset_version_id: datasetVersionId,
        job_type: jobType,
        params: { evalue: parseFloat(evalue) },
        reference_db: refDb,
      }, tenantId);

      onJobSubmitted(res.job_id);
    } catch (err: any) {
      setErrorMsg(err.message || 'Job submission failed');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.5rem', marginBottom: '1.5rem' }}>
      <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#f8fafc', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Settings2 color="#a78bfa" size={22} />
        Nextflow Scientific Job Dispatcher
      </h2>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginBottom: '1.25rem' }}>
        <div>
          <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.25rem' }}>Pipeline / Engine</label>
          <select
            value={jobType}
            onChange={(e) => setJobType(e.target.value)}
            style={{ width: '100%', background: '#0f172a', color: '#f8fafc', border: '1px solid #475569', borderRadius: '6px', padding: '0.5rem' }}
          >
            <option value="dna_alpha">Nextflow DNA Alpha (BLAST + Parquet)</option>
            <option value="blast">NCBI BLAST+ Nucleotide Search</option>
            <option value="diamond">DIAMOND High-Throughput Protein Search</option>
            <option value="hmmer">HMMER Profile Domain Scanner</option>
          </select>
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.25rem' }}>Reference Database</label>
          <select
            value={refDb}
            onChange={(e) => setRefDb(e.target.value)}
            style={{ width: '100%', background: '#0f172a', color: '#f8fafc', border: '1px solid #475569', borderRadius: '6px', padding: '0.5rem' }}
          >
            <option value="ncbi_refseq_core_v1">NCBI RefSeq Core Genome (v1)</option>
            <option value="uniprot_swissprot_2026">UniProtKB / Swiss-Prot 2026</option>
            <option value="pfam_domain_profiles_36">Pfam-A Hidden Markov Models (v36)</option>
          </select>
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.25rem' }}>E-Value Cutoff</label>
          <input
            type="number"
            step="0.1"
            value={evalue}
            onChange={(e) => setEvalue(e.target.value)}
            style={{ width: '100%', background: '#0f172a', color: '#f8fafc', border: '1px solid #475569', borderRadius: '6px', padding: '0.5rem' }}
          />
        </div>
      </div>

      <button
        onClick={handleSubmit}
        disabled={!datasetVersionId || submitting}
        style={{
          background: !datasetVersionId ? '#475569' : '#8b5cf6',
          color: '#ffffff',
          fontWeight: 600,
          border: 'none',
          borderRadius: '8px',
          padding: '0.6rem 1.25rem',
          cursor: !datasetVersionId ? 'not-allowed' : 'pointer',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
        }}
      >
        <Play size={16} />
        {submitting ? 'Submitting to Nextflow...' : 'Dispatch Scientific Analysis'}
      </button>

      {!datasetVersionId && (
        <span style={{ display: 'inline-block', marginTop: '0.5rem', fontSize: '0.8rem', color: '#94a3b8' }}>
          * Upload and validate a biological dataset first before dispatching compute.
        </span>
      )}

      {errorMsg && (
        <div style={{ marginTop: '0.75rem', color: '#f87171', fontSize: '0.875rem' }}>
          {errorMsg}
        </div>
      )}
    </div>
  );
};
