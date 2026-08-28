const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, options);
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`${res.status}: ${detail}`);
  }
  return res.json();
}

export const api = {
  health: () => request('/api/health'),

  predict: (payload) =>
    request('/api/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }),

  predictBatch: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return request('/api/predict/batch', { method: 'POST', body: formData });
  },

  modelMetrics: () => request('/api/model/metrics'),

  advanceOffer: (payload) =>
    request('/api/advance/offer', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }),

  auditLog: () => request('/api/audit/log'),

  auditLogCsvUrl: () => `${BASE_URL}/api/audit/log/csv`,
};
