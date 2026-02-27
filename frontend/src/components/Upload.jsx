import React, { useState } from 'react'
import { submitAnalysis } from '../api/client'

export default function Upload({ onSubmit, onDemo }) {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleSubmit(e) {
    e.preventDefault()
    if (!url.trim()) return
    setLoading(true)
    setError(null)
    try {
      const result = await submitAnalysis(url.trim())
      onSubmit(result.analysis_id)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col items-center justify-center py-16">
      {/* Hero */}
      <div className="text-center mb-12">
        <h2 className="text-4xl font-bold mb-4">
          <span className="text-primary-400">Earnings Call</span> Intelligence
        </h2>
        <p className="text-gray-400 text-lg max-w-2xl">
          Upload any earnings call and get a structured intelligence brief in under 2 minutes.
          Voice analysis, entity extraction, visual insights, and fact-checked claims.
        </p>
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="w-full max-w-2xl">
        <div className="card">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Earnings Call URL
          </label>
          <div className="flex gap-3">
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://youtube.com/watch?v=..."
              className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !url.trim()}
              className="bg-primary-600 hover:bg-primary-700 text-white px-6 py-3 rounded-lg font-medium transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Analyzing...' : 'Analyze'}
            </button>
          </div>
          {error && (
            <p className="text-red-400 text-sm mt-2">{error}</p>
          )}
        </div>
      </form>

      {/* Demo button */}
      <button
        onClick={onDemo}
        className="mt-6 text-sm text-primary-400 hover:text-primary-300 transition underline underline-offset-4"
      >
        Load demo: Apple Q4 2024 Earnings Call
      </button>

      {/* How it works */}
      <div className="grid grid-cols-4 gap-4 mt-16 w-full max-w-4xl">
        {[
          { icon: 'V', label: 'Reka Vision', desc: 'Analyzes slides, charts & visual content' },
          { icon: 'M', label: 'Modulate', desc: 'Detects speaker confidence & tone shifts' },
          { icon: 'F', label: 'Fastino', desc: 'Extracts entities & financial metrics' },
          { icon: 'Y', label: 'Yutori', desc: 'Fact-checks claims against public data' },
        ].map((svc) => (
          <div key={svc.label} className="card text-center">
            <div className="w-12 h-12 bg-primary-900/50 rounded-lg flex items-center justify-center text-primary-400 font-bold text-lg mx-auto mb-3">
              {svc.icon}
            </div>
            <h3 className="text-sm font-semibold text-white mb-1">{svc.label}</h3>
            <p className="text-xs text-gray-500">{svc.desc}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
