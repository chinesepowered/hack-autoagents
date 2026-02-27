import React from 'react'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'

export default function VoiceTimeline({ segments }) {
  if (!segments.length) return null

  const chartData = segments.map((seg) => ({
    time: formatTime(seg.start_time),
    confidence: Math.round((seg.confidence_score || 0) * 100),
    speaker: seg.speaker,
    tone: seg.tone,
    transcript: seg.transcript,
  }))

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Voice Confidence Timeline</h3>
        <span className="text-xs text-gray-500">Powered by Modulate</span>
      </div>

      {/* Chart */}
      <div className="h-48 mb-6">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="confidenceGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#5c7cfa" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#5c7cfa" stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis
              dataKey="time"
              tick={{ fill: '#6b7280', fontSize: 11 }}
              axisLine={{ stroke: '#374151' }}
            />
            <YAxis
              domain={[0, 100]}
              tick={{ fill: '#6b7280', fontSize: 11 }}
              axisLine={{ stroke: '#374151' }}
              tickFormatter={(v) => `${v}%`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1f2937',
                border: '1px solid #374151',
                borderRadius: '8px',
                fontSize: '12px',
              }}
              labelStyle={{ color: '#9ca3af' }}
              formatter={(value) => [`${value}%`, 'Confidence']}
            />
            <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="3 3" label="" />
            <Area
              type="monotone"
              dataKey="confidence"
              stroke="#5c7cfa"
              fill="url(#confidenceGrad)"
              strokeWidth={2}
              dot={{ fill: '#5c7cfa', r: 4 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Segment list */}
      <div className="space-y-3 max-h-64 overflow-y-auto">
        {segments.map((seg) => (
          <div key={seg.id} className="flex gap-3 text-sm">
            <div className="w-16 shrink-0 text-gray-500 text-xs pt-1">
              {formatTime(seg.start_time)}
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="font-medium text-gray-200">{seg.speaker}</span>
                <span className={`badge ${getToneBadge(seg.tone)}`}>
                  {seg.tone}
                </span>
                <span className="text-xs text-gray-500">
                  {Math.round((seg.confidence_score || 0) * 100)}% confidence
                </span>
              </div>
              <p className="text-gray-400 text-xs leading-relaxed">
                {seg.transcript}
              </p>
            </div>
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

function getToneBadge(tone) {
  const map = {
    confident: 'badge-verified',
    enthusiastic: 'bg-blue-900/50 text-blue-300 border border-blue-700',
    neutral: 'bg-gray-800 text-gray-400 border border-gray-600',
    measured: 'badge-context',
    evasive: 'badge-disputed',
  }
  return map[tone] || 'badge-unverified'
}
