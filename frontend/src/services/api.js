const PRODUCTION_API_URL = 'https://datamind-e5zu.onrender.com';
const DEVELOPMENT_API_URL = 'http://localhost:8000';

const configuredUrl = import.meta.env.VITE_API_URL?.trim();
const API_BASE = (configuredUrl || (import.meta.env.DEV ? DEVELOPMENT_API_URL : PRODUCTION_API_URL)).replace(/\/$/, '');

function readableError(payload, status) {
  if (typeof payload?.detail === 'string') return payload.detail;
  if (Array.isArray(payload?.detail)) {
    return payload.detail.map((item) => item.msg || 'Invalid request').join('; ');
  }
  if (typeof payload?.message === 'string') return payload.message;
  if (status === 429) return 'Too many requests. Please wait briefly and try again.';
  if (status >= 500) return 'DataMind server had a temporary problem. Please retry.';
  return `Request failed (${status}). Please check the input and try again.`;
}

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...options,
      method: options.method || 'GET',
      cache: 'no-store',
      credentials: 'omit',
      headers: options.body instanceof FormData
        ? { Accept: 'application/json', ...(options.headers || {}) }
        : { Accept: 'application/json', 'Content-Type': 'application/json', ...(options.headers || {}) },
    });
  } catch (error) {
    const isNetwork = error instanceof TypeError;
    throw new Error(isNetwork
      ? `Cannot connect to DataMind API at ${API_BASE}. Check that the Render service is awake and that ALLOWED_ORIGINS includes this website.`
      : (error?.message || 'Network request failed.'));
  }

  const contentType = response.headers.get('content-type') || '';
  let payload = {};
  if (contentType.includes('application/json')) {
    try { payload = await response.json(); } catch { payload = {}; }
  } else {
    const text = await response.text().catch(() => '');
    if (text && response.status >= 400) payload = { detail: text.slice(0, 350) };
  }

  if (!response.ok) throw new Error(readableError(payload, response.status));
  if (!payload || typeof payload !== 'object') throw new Error('DataMind API returned an invalid response.');
  return payload;
}

export const getApiBase = () => API_BASE;
export const getHealth = () => request('/api/health');
export const transformText = (body) => request('/api/transform', { method: 'POST', body: JSON.stringify(body) });

export function transformFile(file, settings) {
  const form = new FormData();
  form.append('file', file);
  Object.entries(settings).forEach(([key, value]) => form.append(key, String(value)));
  return request('/api/transform/file', { method: 'POST', body: form });
}

export const refineResult = (body) => request('/api/refine', { method: 'POST', body: JSON.stringify(body) });
