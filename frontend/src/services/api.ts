const API_BASE = '/api/v1'

function headers() {
  const token = localStorage.getItem('token')
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }
}

async function fetchJson(input: string, init?: RequestInit) {
  const res = await fetch(input, { ...init, headers: { ...headers(), ...(init?.headers || {}) } })
  if (!res.ok) {
    const err = await res.text()
    throw new Error(err)
  }
  return res.json()
}

export const AuthAPI = {
  loginUrl: () => fetchJson(`${API_BASE}/auth/login`),
  callback: (code: string) => fetchJson(`${API_BASE}/auth/callback?code=${code}`, { method: 'POST' }),
  me: () => fetchJson(`${API_BASE}/auth/me`),
}

export const RepoAPI = {
  list: () => fetchJson(`${API_BASE}/repos`),
  add: (owner: string, name: string) => fetchJson(`${API_BASE}/repos/${owner}/${name}/add`, { method: 'POST' }),
}

export const ScanAPI = {
  trigger: (repository_id: number, branch = 'main') =>
    fetchJson(`${API_BASE}/scans`, { method: 'POST', body: JSON.stringify({ repository_id, branch }) }),
  get: (id: number) => fetchJson(`${API_BASE}/scans/${id}`),
}

export const FindingAPI = {
  list: (params?: Record<string, string>) => {
    const qs = params ? '?' + new URLSearchParams(params).toString() : ''
    return fetchJson(`${API_BASE}/findings${qs}`)
  },
}

export const DashboardAPI = {
  metrics: () => fetchJson(`${API_BASE}/dashboard/metrics`),
}
