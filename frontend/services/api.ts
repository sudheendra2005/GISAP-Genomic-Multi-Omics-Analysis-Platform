const API_BASE = '/api/v1';

export interface PresignRequest {
  project_id: string;
  name: string;
  sequence_type: 'dna' | 'rna' | 'protein';
  format: 'fasta' | 'fastq';
  filename: string;
}

export interface JobSubmission {
  project_id: string;
  dataset_version_id: string;
  job_type: string;
  params?: Record<string, any>;
  reference_db?: string;
}

export const apiService = {
  async presign(req: PresignRequest, tenantId: string) {
    const res = await fetch(`${API_BASE}/datasets/presign`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Tenant-ID': tenantId,
      },
      body: JSON.stringify(req),
    });
    if (!res.ok) throw new Error(`Failed to request presigned upload: ${res.statusText}`);
    return res.json();
  },

  async uploadDirect(bucket: string, key: string, file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/datasets/upload-direct?bucket=${bucket}&key=${key}`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) throw new Error(`Upload failed: ${res.statusText}`);
    return res.json();
  },

  async validate(datasetId: string, tenantId: string) {
    const res = await fetch(`${API_BASE}/datasets/${datasetId}/validate`, {
      method: 'POST',
      headers: { 'X-Tenant-ID': tenantId },
    });
    if (!res.ok) throw new Error(`Validation failed: ${res.statusText}`);
    return res.json();
  },

  async submitJob(sub: JobSubmission, tenantId: string) {
    const res = await fetch(`${API_BASE}/jobs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Tenant-ID': tenantId,
      },
      body: JSON.stringify(sub),
    });
    if (!res.ok) throw new Error(`Job submission failed: ${res.statusText}`);
    return res.json();
  },

  async getJobStatus(jobId: string, tenantId: string) {
    const res = await fetch(`${API_BASE}/jobs/${jobId}`, {
      headers: { 'X-Tenant-ID': tenantId },
    });
    if (!res.ok) throw new Error(`Failed to get status: ${res.statusText}`);
    return res.json();
  },

  async getJobResults(jobId: string, tenantId: string) {
    const res = await fetch(`${API_BASE}/jobs/${jobId}/results`, {
      headers: { 'X-Tenant-ID': tenantId },
    });
    if (!res.ok) throw new Error(`Failed to get results: ${res.statusText}`);
    return res.json();
  },

  async getJobProvenance(jobId: string, tenantId: string) {
    const res = await fetch(`${API_BASE}/jobs/${jobId}/provenance`, {
      headers: { 'X-Tenant-ID': tenantId },
    });
    if (!res.ok) throw new Error(`Failed to get provenance: ${res.statusText}`);
    return res.json();
  },
};
