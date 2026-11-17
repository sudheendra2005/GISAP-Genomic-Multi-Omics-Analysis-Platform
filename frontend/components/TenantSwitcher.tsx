import React from 'react';
import { Building2 } from 'lucide-react';

interface TenantSwitcherProps {
  currentTenant: string;
  onTenantChange: (tenant: string) => void;
}

export const TenantSwitcher: React.FC<TenantSwitcherProps> = ({ currentTenant, onTenantChange }) => {
  const tenants = [
    { id: 'ssit-tumakuru', label: 'SSIT Tumakuru (Sri Siddhartha Institute)' },
    { id: 'gisap-research', label: 'GISAP Central Research Lab' },
    { id: 'oncology-consortium', label: 'Clinical Oncology Consortium' },
  ];

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.5rem 1rem', background: '#1e293b', borderRadius: '8px', border: '1px solid #334155' }}>
      <Building2 size={18} color="#60a5fa" />
      <span style={{ fontSize: '0.875rem', color: '#94a3b8', fontWeight: 500 }}>Active Tenant:</span>
      <select
        value={currentTenant}
        onChange={(e) => onTenantChange(e.target.value)}
        style={{
          background: '#0f172a',
          color: '#f8fafc',
          border: '1px solid #475569',
          borderRadius: '6px',
          padding: '0.25rem 0.5rem',
          fontSize: '0.875rem',
          outline: 'none',
          cursor: 'pointer',
        }}
      >
        {tenants.map((t) => (
          <option key={t.id} value={t.id}>{t.label}</option>
        ))}
      </select>
    </div>
  );
};
