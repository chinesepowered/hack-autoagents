import React from 'react'
import Summary from './Summary'
import EntityList from './EntityList'
import VoiceTimeline from './VoiceTimeline'
import VisualInsights from './VisualInsights'
import FactChecks from './FactChecks'

export default function Dashboard({ analysis }) {
  return (
    <div className="space-y-6">
      {/* Title bar */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">{analysis.title}</h2>
          <p className="text-sm text-gray-500 mt-1">
            {analysis.source_url && (
              <span className="truncate max-w-md inline-block align-bottom">
                {analysis.source_url}
              </span>
            )}
          </p>
        </div>
        <span className="badge badge-verified">Completed</span>
      </div>

      {/* Summary */}
      <Summary text={analysis.summary} />

      {/* Two-column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Voice Timeline */}
        <VoiceTimeline segments={analysis.voice_segments || []} />

        {/* Entity List */}
        <EntityList entities={analysis.entities || []} />
      </div>

      {/* Full-width sections */}
      <FactChecks checks={analysis.fact_checks || []} />
      <VisualInsights segments={analysis.visual_segments || []} />
    </div>
  )
}
