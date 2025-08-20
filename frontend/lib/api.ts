export async function apiFetch(path: string, options: RequestInit = {}) {
  const base = process.env.NEXT_PUBLIC_API_BASE_URL || '';
  const headers = new Headers(options.headers);
  if (typeof window !== 'undefined') {
    const tenant = localStorage.getItem('tenantId');
    if (tenant) headers.set('X-Tenant-ID', tenant);
  }
  if (!headers.has('Content-Type') && options.body) {
    headers.set('Content-Type', 'application/json');
  }
  return fetch(base + path, { ...options, headers });
}
