import React from 'react'

const TYPE_ICONS = {
  slide: 'S',
  chart: 'C',
  speaker: 'P',
  product_demo: 'D',
  other: '?',
}

const TYPE_COLORS = {
  slide: 'bg-blue-900/50 text-blue-400 border-blue-700',
  chart: 'bg-green-900/50 text-green-400 border-green-700',
  speaker: 'bg-purple-900/50 text-purple-400 border-purple-700',
  product_demo: 'bg-orange-900/50 text-orange-400 border-orange-700',
  other: 'bg-gray-800 text-gray-400 border-gray-600',
}

export default function VisualInsights({ segments }) {
  if (!segments.length) return null

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Visual Content Analysis</h3>
        <span className="text-xs text-gray-500">Powered by Reka Vision</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {segments.map((seg) => (
          <div
            key={seg.id}
            className={`rounded-lg border p-4 ${TYPE_COLORS[seg.content_type] || TYPE_COLORS.other}`}
          >
            <div className="flex items-center gap-2 mb-2">
              <div className="w-8 h-8 rounded flex items-center justify-center bg-black/30 text-sm font-bold">
                {TYPE_ICONS[seg.content_type] || '?'}
              </div>
              <div>
                <span className="text-xs font-medium uppercase tracking-wider">
                  {(seg.content_type || 'unknown').replace(/_/g, ' ')}
                </span>
                <span className="text-xs opacity-60 ml-2">
                  @ {formatTime(seg.timestamp)}
                </span>
              </div>
            </div>
            <p className="text-sm opacity-80 leading-relaxed">
              {seg.description}
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}

function formatTime(seconds) {
  if (!seconds && seconds !== 0) return '0:00'
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}
