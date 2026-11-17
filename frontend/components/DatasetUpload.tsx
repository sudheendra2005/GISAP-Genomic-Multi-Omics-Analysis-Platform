import React, { useState } from 'react';
import { UploadCloud, CheckCircle2, AlertCircle, FileText } from 'lucide-react';
import { apiService } from '../services/api';

interface DatasetUploadProps {
  tenantId: string;
  onValidationComplete: (datasetId: string, versionId: string, sha: string) => void;
}

export const DatasetUpload: React.FC<DatasetUploadProps> = ({ tenantId, onValidationComplete }) => {
  const [file, setFile] = useState<File | null>(null);
  const [seqType, setSeqType] = useState<'dna' | 'rna' | 'protein'>('dna');
  const [format, setFormat] = useState<'fasta' | 'fastq'>('fasta');
  const [status, setStatus] = useState<string>('idle');
  const [result, setResult] = useState<any>(null);
  const [errorMsg, setErrorMsg] = useState<string>('');

  const handleUploadAndValidate = async () => {
    if (!file) return;
    setStatus('uploading');
    setErrorMsg('');

    try {
      // 1. Presign
      const presign = await apiService.presign({
        project_id: 'default-project',
        name: file.name,
        sequence_type: seqType,
        format: format,
        filename: file.name,
      }, tenantId);

      // 2. Direct upload to storage
      const s3Parts = presign.s3_uri.replace('s3://', '').split('/');
      const bucket = s3Parts[0];
      const key = s3Parts.slice(1).join('/');

      await apiService.uploadDirect(bucket, key, file);

      // 3. Streaming validation
      setStatus('validating');
      const val = await apiService.validate(presign.dataset_id, tenantId);

      setResult(val);
      setStatus(val.is_valid ? 'success' : 'invalid');
      if (val.is_valid) {
        onValidationComplete(val.dataset_id, val.version_id, val.sha256_hash);
      }
    } catch (err: any) {
      setStatus('error');
      setErrorMsg(err.message || 'Validation failed');
    }
  };

  return (
    <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.5rem', marginBottom: '1.5rem' }}>
      <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#f8fafc', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <UploadCloud color="#38bdf8" size={22} />
        Biological Sequence Ingestion & O(1) Streaming Validation
      </h2>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.25rem' }}>
        <div>
          <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.25rem' }}>Sequence Type</label>
          <select
            value={seqType}
            onChange={(e) => setSeqType(e.target.value as any)}
            style={{ width: '100%', background: '#0f172a', color: '#f8fafc', border: '1px solid #475569', borderRadius: '6px', padding: '0.5rem' }}
          >
            <option value="dna">DNA (Deoxyribonucleic Acid)</option>
            <option value="rna">RNA (Ribonucleic Acid)</option>
            <option value="protein">Protein (Amino Acid Translation)</option>
          </select>
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.25rem' }}>Format</label>
          <select
            value={format}
            onChange={(e) => setFormat(e.target.value as any)}
            style={{ width: '100%', background: '#0f172a', color: '#f8fafc', border: '1px solid #475569', borderRadius: '6px', padding: '0.5rem' }}
          >
            <option value="fasta">FASTA (.fa, .fasta)</option>
            <option value="fastq">FASTQ (.fq, .fastq)</option>
          </select>
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.25rem' }}>Select Sequence File</label>
          <input
            type="file"
            onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)}
            style={{ width: '100%', fontSize: '0.875rem', color: '#94a3b8', cursor: 'pointer' }}
          />
        </div>
      </div>

      <button
        onClick={handleUploadAndValidate}
        disabled={!file || status === 'uploading' || status === 'validating'}
        style={{
          background: !file ? '#475569' : '#2563eb',
          color: '#ffffff',
          fontWeight: 600,
          border: 'none',
          borderRadius: '8px',
          padding: '0.6rem 1.25rem',
          cursor: !file ? 'not-allowed' : 'pointer',
          transition: 'all 0.15s ease',
        }}
      >
        {status === 'uploading' ? 'Streaming to S3...' : status === 'validating' ? 'Validating in O(1) RAM...' : 'Ingest & Validate Sequence'}
      </button>

      {result && (
        <div style={{ marginTop: '1.25rem', padding: '1rem', background: result.is_valid ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)', border: `1px solid ${result.is_valid ? '#22c55e' : '#ef4444'}`, borderRadius: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
            {result.is_valid ? <CheckCircle2 color="#22c55e" size={20} /> : <AlertCircle color="#ef4444" size={20} />}
            <span style={{ fontWeight: 600, color: result.is_valid ? '#4ade80' : '#f87171' }}>
              {result.is_valid ? 'Validation Passed — Cryptographically Verified' : 'Validation Failed — Corrupted Biological Structure'}
            </span>
          </div>
          <div style={{ fontSize: '0.85rem', color: '#cbd5e1', lineHeight: '1.6' }}>
            <div><strong>SHA-256 Digest:</strong> <code style={{ color: '#38bdf8' }}>{result.sha256_hash}</code></div>
            <div><strong>Parsed Records:</strong> {result.sequence_count} sequences</div>
            <div><strong>Total Base Pairs:</strong> {result.total_bp.toLocaleString()} bp</div>
            {result.errors?.length > 0 && (
              <div style={{ color: '#f87171', marginTop: '0.5rem' }}>
                <strong>Errors:</strong> {result.errors.join(', ')}
              </div>
            )}
          </div>
        </div>
      )}

      {errorMsg && (
        <div style={{ marginTop: '1rem', color: '#f87171', fontSize: '0.875rem' }}>
          Error: {errorMsg}
        </div>
      )}
    </div>
  );
};
