import React, { useState } from 'react';
import { TenantSwitcher } from '../components/TenantSwitcher';
import { DatasetUpload } from '../components/DatasetUpload';
import { JobSubmission } from '../components/JobSubmission';
import { LiveJobStatus } from '../components/LiveJobStatus';
import { BlastHitExplorer } from '../components/BlastHitExplorer';
import { ProvenanceViewer } from '../components/ProvenanceViewer';
import { Dna, Activity, Shield, Layers } from 'lucide-react';

export const App: React.FC = () => {
  const [currentTenant, setCurrentTenant] = useState('ssit-tumakuru');
  const [activeDatasetId, setActiveDatasetId] = useState<string | null>(null);
  const [activeVersionId, setActiveVersionId] = useState<string | null>(null);
  const [activeJobId, setActiveJobId] = useState<string | null>(null);

  const handleValidationComplete = (dsId: string, verId: string, _sha: string) => {
    setActiveDatasetId(dsId);
    setActiveVersionId(verId);
  };

  const handleJobSubmitted = (jobId: string) => {
    setActiveJobId(jobId);
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem 1rem', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
      {/* Header */}
      <header style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', paddingBottom: '1rem', borderBottom: '1px solid #334155' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <Dna color="#38bdf8" size={32} />
            GISAP Platform
          </h1>
          <p style={{ fontSize: '0.875rem', color: '#94a3b8', marginTop: '0.25rem' }}>
            Genomic & Multi-Omics Analysis Platform — Unified Source of Truth
          </p>
        </div>

        <TenantSwitcher currentTenant={currentTenant} onTenantChange={setCurrentTenant} />
      </header>

      {/* Main Panels */}
      <main>
        {/* 1. Dataset Ingestion */}
        <DatasetUpload tenantId={currentTenant} onValidationComplete={handleValidationComplete} />

        {/* 2. Job Dispatcher */}
        <JobSubmission tenantId={currentTenant} datasetVersionId={activeVersionId} onJobSubmitted={handleJobSubmitted} />

        {/* 3. Real-Time Execution Tracking */}
        <LiveJobStatus tenantId={currentTenant} jobId={activeJobId} onJobCompleted={handleJobSubmitted} />

        {/* 4. BLAST Structured Hits */}
        <BlastHitExplorer tenantId={currentTenant} jobId={activeJobId} />

        {/* 5. Provenance Graph Lineage */}
        <ProvenanceViewer tenantId={currentTenant} jobId={activeJobId} />
      </main>

      {/* Footer */}
      <footer style={{ marginTop: '3rem', paddingTop: '1.5rem', borderTop: '1px solid #1e293b', textAlign: 'center', color: '#64748b', fontSize: '0.8rem' }}>
        GISAP Alpha v1.0.0 &bull; Built with React + TypeScript &bull; Separated Compute & Storage Architecture
      </footer>
    </div>
  );
};

export default App;
