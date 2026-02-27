import React, { useState, useEffect, useCallback } from 'react'
import Upload from './components/Upload'
import Dashboard from './components/Dashboard'
import { getAnalysis, getAnalysisStatus } from './api/client'

export default function App() {
  const [analysisId, setAnalysisId] = useState(null)
  const [analysis, setAnalysis] = useState(null)
  const [status, setStatus] = useState(null)
  const [error, setError] = useState(null)

  const pollStatus = useCallback(async () => {
    if (!analysisId) return
    try {
      const s = await getAnalysisStatus(analysisId)
      setStatus(s.status)
      if (s.status === 'completed' || s.status === 'failed') {
        const full = await getAnalysis(analysisId)
        setAnalysis(full)
      }
    } catch (e) {
      setError(e.message)
    }
  }, [analysisId])

  useEffect(() => {
    if (!analysisId || status === 'completed' || status === 'failed') return
    const interval = setInterval(pollStatus, 2000)
    return () => clearInterval(interval)
  }, [analysisId, status, pollStatus])

  function handleSubmit(id) {
    setAnalysisId(id)
    setStatus('processing')
    setAnalysis(null)
    setError(null)
  }

  function handleReset() {
    setAnalysisId(null)
    setAnalysis(null)
    setStatus(null)
    setError(null)
  }

  // Load demo data for hackathon presentation
  function handleDemo() {
    setAnalysis(DEMO_DATA)
    setStatus('completed')
    setAnalysisId('demo')
  }

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-950/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center text-xl">
              E
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">EchoMind</h1>
              <p className="text-xs text-gray-500">Earnings Call Intelligence Engine</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {analysisId && (
              <button
                onClick={handleReset}
                className="text-sm text-gray-400 hover:text-white transition"
              >
                New Analysis
              </button>
            )}
            <div className="flex gap-1">
              {['Reka', 'Modulate', 'Fastino', 'Yutori', 'Render'].map((s) => (
                <span key={s} className="text-[10px] px-1.5 py-0.5 bg-gray-800 rounded text-gray-500">
                  {s}
                </span>
              ))}
            </div>
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {!analysisId && !analysis && (
          <Upload onSubmit={handleSubmit} onDemo={handleDemo} />
        )}

        {status === 'processing' && (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="w-16 h-16 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mb-6" />
            <h2 className="text-xl font-semibold mb-2">Analyzing Earnings Call</h2>
            <p className="text-gray-500 text-sm">Running 4 AI services in parallel...</p>
            <div className="mt-6 flex gap-4">
              {[
                { name: 'Reka Vision', desc: 'Analyzing video frames' },
                { name: 'Modulate', desc: 'Voice patterns' },
                { name: 'Fastino', desc: 'Entity extraction' },
                { name: 'Yutori', desc: 'Fact-checking claims' },
              ].map((svc) => (
                <div key={svc.name} className="card text-center px-4 py-3">
                  <div className="text-xs font-medium text-primary-400">{svc.name}</div>
                  <div className="text-[10px] text-gray-500 mt-1">{svc.desc}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-900/20 border border-red-800 rounded-lg p-4 text-red-300 mt-4">
            {error}
          </div>
        )}

        {analysis && status === 'completed' && <Dashboard analysis={analysis} />}
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-800 mt-16 py-6 text-center text-xs text-gray-600">
        Built with Reka Vision + Modulate + Fastino/GLiNER2 + Yutori | Deployed on Render
      </footer>
    </div>
  )
}

// Demo data for hackathon presentation
const DEMO_DATA = {
  id: 'demo-001',
  title: 'Apple Q4 2024 Earnings Call Analysis',
  source_url: 'https://example.com/apple-q4-2024-earnings',
  status: 'completed',
  summary: `## Executive Summary

**Speakers identified:** Tim Cook, Luca Maestri
**Companies mentioned:** Apple Inc.
**Key metrics:** $110.2 billion, 23%, 46.2%, 1 billion paid subscriptions, $65.8 billion

### Voice Analysis
Average speaker confidence: 83%
**Notable:** 1 segment flagged with below-average confidence, particularly during Q&A on margins and competitive positioning.

### Fact Check Results
- **2** claims verified against public data
- **0** claims disputed or needing context
- **3** claims unverified

### Visual Content
Detected **2** charts/graphs and **2** presentation slides.`,
  entities: [
    { id: '1', name: 'Tim Cook', entity_type: 'person', context: 'CEO presenting quarterly results', confidence: 0.97 },
    { id: '2', name: 'Luca Maestri', entity_type: 'person', context: 'CFO discussing financials', confidence: 0.95 },
    { id: '3', name: 'Apple Inc.', entity_type: 'company', context: 'Parent company reporting earnings', confidence: 0.99 },
    { id: '4', name: '$110.2 billion', entity_type: 'currency_amount', context: 'Total quarterly revenue', confidence: 0.96 },
    { id: '5', name: '23%', entity_type: 'percentage', context: 'Year-over-year revenue growth', confidence: 0.94 },
    { id: '6', name: 'iPhone', entity_type: 'product', context: 'Flagship product line', confidence: 0.98 },
    { id: '7', name: 'Services', entity_type: 'market_segment', context: 'Fastest growing business segment', confidence: 0.93 },
    { id: '8', name: 'Q4 2024', entity_type: 'date', context: 'Reporting period', confidence: 0.99 },
    { id: '9', name: '1 billion paid subscriptions', entity_type: 'financial_metric', context: 'Services ecosystem scale', confidence: 0.91 },
    { id: '10', name: '46.2%', entity_type: 'percentage', context: 'Gross margin for the quarter', confidence: 0.95 },
    { id: '11', name: 'We expect improvement in Q1', entity_type: 'forward_looking_statement', context: 'CFO guidance on margin trajectory', confidence: 0.87 },
    { id: '12', name: 'Component cost headwinds', entity_type: 'risk_factor', context: 'Pressure on hardware margins', confidence: 0.82 },
  ],
  voice_segments: [
    { id: '1', start_time: 0, end_time: 45, speaker: 'CEO - Tim Cook', confidence_score: 0.92, tone: 'confident', transcript: 'Good afternoon everyone. Thank you for joining us for our Q4 2024 earnings call. We\'re thrilled to report another record quarter.' },
    { id: '2', start_time: 45, end_time: 120, speaker: 'CFO - Luca Maestri', confidence_score: 0.88, tone: 'confident', transcript: 'Total revenue for the quarter reached $110.2 billion, up 23% year over year. Our Services business continues to accelerate.' },
    { id: '3', start_time: 120, end_time: 180, speaker: 'CEO - Tim Cook', confidence_score: 0.85, tone: 'enthusiastic', transcript: 'Our product pipeline has never been stronger. We\'re seeing incredible adoption of our AI features across the ecosystem.' },
    { id: '4', start_time: 180, end_time: 240, speaker: 'Analyst - Morgan Stanley', confidence_score: 0.78, tone: 'neutral', transcript: 'Can you speak to the margin pressure we\'re seeing in the hardware segment? What\'s the outlook for next quarter?' },
    { id: '5', start_time: 240, end_time: 300, speaker: 'CEO - Tim Cook', confidence_score: 0.65, tone: 'evasive', transcript: 'We\'re always looking at ways to optimize our cost structure. The overall picture is very positive and we remain confident in our trajectory.' },
    { id: '6', start_time: 300, end_time: 360, speaker: 'CFO - Luca Maestri', confidence_score: 0.82, tone: 'measured', transcript: 'Gross margins came in at 46.2%, slightly below expectations due to component costs, but we expect improvement in Q1.' },
    { id: '7', start_time: 360, end_time: 420, speaker: 'Analyst - Goldman Sachs', confidence_score: 0.75, tone: 'neutral', transcript: 'What\'s driving the acceleration in Services revenue? Can you break down the contribution from the App Store versus subscriptions?' },
    { id: '8', start_time: 420, end_time: 480, speaker: 'CEO - Tim Cook', confidence_score: 0.91, tone: 'confident', transcript: 'Services is truly a growth engine for us. We now have over 1 billion paid subscriptions across our platform. The ecosystem flywheel is working.' },
  ],
  visual_segments: [
    { id: '1', timestamp: 0, description: "Title slide: 'Q4 2024 Earnings Call' with company logo and date", content_type: 'slide' },
    { id: '2', timestamp: 30, description: 'Revenue chart showing 23% YoY growth, from $89.5B to $110.2B', content_type: 'chart' },
    { id: '3', timestamp: 60, description: 'CEO speaking at podium, confident posture, gesturing at screen', content_type: 'speaker' },
    { id: '4', timestamp: 90, description: 'Product roadmap slide showing 3 new product launches planned for Q1 2025', content_type: 'slide' },
    { id: '5', timestamp: 120, description: 'Operating margin chart: improved from 29.8% to 33.1%, with Services segment highlighted', content_type: 'chart' },
  ],
  fact_checks: [
    { id: '1', claim: 'Total revenue reached $110.2 billion, up 23% year over year', verdict: 'verified', evidence: 'SEC filing 10-Q confirms Q4 2024 revenue of $110.2B vs $89.5B in Q4 2023, representing 23.1% YoY growth.', sources: '["https://investor.apple.com/sec-filings/"]' },
    { id: '2', claim: 'Over 1 billion paid subscriptions across the platform', verdict: 'verified', evidence: 'Apple reported crossing 1 billion paid subscriptions in Q3 2024. This figure includes Apple Music, iCloud, Apple TV+, and third-party subscriptions.', sources: '["https://www.apple.com/newsroom/"]' },
    { id: '3', claim: 'Gross margins at 46.2%, slightly below expectations', verdict: 'context_needed', evidence: 'Gross margin of 46.2% is confirmed, but analyst consensus was 46.5%. The 30bps miss is within normal variance.', sources: '["https://finance.yahoo.com/quote/AAPL/"]' },
    { id: '4', claim: 'Product pipeline has never been stronger', verdict: 'unverified', evidence: 'Subjective forward-looking statement. Apple has announced Vision Pro 2, M4 chips, and AI features, but "never been stronger" is not objectively verifiable.', sources: '[]' },
    { id: '5', claim: 'We expect margin improvement in Q1', verdict: 'context_needed', evidence: 'Forward-looking guidance. Historical data shows Q1 typically has higher margins due to holiday mix. Component cost trends suggest 50-80bps improvement possible.', sources: '["https://finance.yahoo.com/quote/AAPL/"]' },
  ],
}
