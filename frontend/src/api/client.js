const API_BASE = import.meta.env.VITE_API_URL || ''

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
