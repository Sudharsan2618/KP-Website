export type CmsEnvelope<T> = { data: T };

const cmsUrl = (import.meta.env.CMS_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');

export async function cmsFetch<T>(path: string): Promise<T> {
  const response = await fetch(`${cmsUrl}${path}`, { headers: { accept: 'application/json' } });
  if (!response.ok) throw new Error(`CMS request failed: ${response.status}`);
  const payload = (await response.json()) as CmsEnvelope<T> | T;
  return (payload && typeof payload === 'object' && 'data' in payload ? payload.data : payload) as T;
}

export async function getPage(path: string) {
  return cmsFetch<Record<string, unknown>>(`/api/v1/pages/by-path/?path=${encodeURIComponent(path)}`);
}

export async function getSiteSettings() {
  return cmsFetch<Record<string, unknown>>('/api/v1/site-settings/');
}

export async function getJobs(query = '') {
  return cmsFetch<{ data: Record<string, unknown>[]; meta: Record<string, unknown>; facets?: Record<string, unknown> }>(`/api/v1/jobs/${query ? `?${query}` : ''}`);
}
