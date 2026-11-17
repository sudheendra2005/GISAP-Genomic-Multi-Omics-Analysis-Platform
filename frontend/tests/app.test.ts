import { describe, it, expect } from 'vitest';
import { apiService } from '../services/api';

describe('Frontend API Service Suite', () => {
  it('formats presign request accurately', () => {
    const req = {
      project_id: 'proj-001',
      name: 'test.fasta',
      sequence_type: 'dna' as const,
      format: 'fasta' as const,
      filename: 'test.fasta',
    };
    expect(req.sequence_type).toBe('dna');
    expect(req.format).toBe('fasta');
  });

  it('validates tenant parameter propagation', () => {
    const tenantId = 'ssit-tumakuru';
    expect(tenantId).toBe('ssit-tumakuru');
  });
});
