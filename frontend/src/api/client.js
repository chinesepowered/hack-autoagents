// VITE_API_URL may be a bare hostname (from Render's fromService host property)
// or a full URL. Normalise to always have https:// in production.
const _raw = import.meta.env.VITE_API_URL || ''
const API_BASE = _raw && !_raw.startsWith('http') ? `https://${_raw}` : _raw

export async function submitAnalysis(url) {
  const res = await fetch(`${API_BASE}/api/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  })
  if (!res.ok) throw new Error(`Failed to submit: ${res.statusText}`)
  return res.json()
}

export async function getAnalysis(id) {
  const res = await fetch(`${API_BASE}/api/analysis/${id}`)
  if (!res.ok) throw new Error(`Failed to fetch: ${res.statusText}`)
  return res.json()
}

export async function getAnalysisStatus(id) {
  const res = await fetch(`${API_BASE}/api/analysis/${id}/status`)
  if (!res.ok) throw new Error(`Failed to fetch status: ${res.statusText}`)
  return res.json()
}

export async function listAnalyses() {
  const res = await fetch(`${API_BASE}/api/analyses`)
  if (!res.ok) throw new Error(`Failed to list: ${res.statusText}`)
  return res.json()
}
