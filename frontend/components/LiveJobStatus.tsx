import React, { useEffect, useState } from 'react';
import { Loader2, CheckCircle2, XCircle, Clock } from 'lucide-react';
import { apiService } from '../services/api';

interface LiveJobStatusProps {
  tenantId: string;
  jobId: string | null;
  onJobCompleted: (jobId: string) => void;
}

export const LiveJobStatus: React.FC<LiveJobStatusProps> = ({ tenantId, jobId, onJobCompleted }) => {
  const [jobInfo, setJobInfo] = useState<any>(null);

  useEffect(() => {
    if (!jobId) return;

    let active = true;
    const poll = async () => {
      try {
        const info = await apiService.getJobStatus(jobId, tenantId);
        if (active) {
          setJobInfo(info);
          if (info.status === 'completed') {
            onJobCompleted(jobId);
          } else if (info.status === 'failed') {
            // Stopped polling on failure
          } else {
            setTimeout(poll, 1500);
          }
        }
      } catch (e) {
        if (active) setTimeout(poll, 2500);
      }
    };

    poll();
    return () => { active = false; };
  }, [jobId, tenantId]);

  if (!jobId || !jobInfo) return null;

  return (
    <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem', marginBottom: '1.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>Job ID: <code>{jobId}</code></span>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#f8fafc', marginTop: '0.2rem' }}>
            Pipeline Status: <span style={{ textTransform: 'uppercase', color: jobInfo.status === 'completed' ? '#4ade80' : jobInfo.status === 'failed' ? '#f87171' : '#38bdf8' }}>{jobInfo.status}</span>
          </h3>
        </div>

        <div>
          {jobInfo.status === 'running' || jobInfo.status === 'pending' ? (
            <Loader2 className="animate-spin" color="#38bdf8" size={26} />
          ) : jobInfo.status === 'completed' ? (
            <CheckCircle2 color="#4ade80" size={26} />
          ) : (
            <XCircle color="#f87171" size={26} />
          )}
        </div>
      </div>

      {jobInfo.s3_output_uri && (
        <div style={{ marginTop: '0.75rem', fontSize: '0.85rem', color: '#cbd5e1' }}>
          <strong>S3 Parquet Artifact:</strong> <code style={{ color: '#38bdf8' }}>{jobInfo.s3_output_uri}</code>
        </div>
      )}

      {jobInfo.error_message && (
        <div style={{ marginTop: '0.75rem', padding: '0.5rem', background: 'rgba(239, 68, 68, 0.2)', border: '1px solid #ef4444', borderRadius: '6px', color: '#f87171', fontSize: '0.85rem' }}>
          Error: {jobInfo.error_message}
        </div>
      )}
    </div>
  );
};
