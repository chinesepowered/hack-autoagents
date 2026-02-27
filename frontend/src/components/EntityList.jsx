import React from 'react'

const TYPE_COLORS = {
  person: 'bg-blue-900/50 text-blue-300 border-blue-700',
  company: 'bg-purple-900/50 text-purple-300 border-purple-700',
  currency_amount: 'bg-green-900/50 text-green-300 border-green-700',
  percentage: 'bg-emerald-900/50 text-emerald-300 border-emerald-700',
  product: 'bg-orange-900/50 text-orange-300 border-orange-700',
  market_segment: 'bg-cyan-900/50 text-cyan-300 border-cyan-700',
  date: 'bg-gray-800 text-gray-300 border-gray-600',
  financial_metric: 'bg-yellow-900/50 text-yellow-300 border-yellow-700',
  forward_looking_statement: 'bg-red-900/50 text-red-300 border-red-700',
  risk_factor: 'bg-rose-900/50 text-rose-300 border-rose-700',
}

export default function EntityList({ entities }) {
  if (!entities.length) return null

  // Group by type
  const grouped = {}
  for (const entity of entities) {
    const type = entity.entity_type || 'other'
    if (!grouped[type]) grouped[type] = []
    grouped[type].push(entity)
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Extracted Entities</h3>
        <span className="text-xs text-gray-500">Powered by Fastino/GLiNER2</span>
      </div>

      <div className="space-y-4">
        {Object.entries(grouped).map(([type, ents]) => (
          <div key={type}>
            <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
              {type.replace(/_/g, ' ')}
            </h4>
            <div className="flex flex-wrap gap-2">
              {ents.map((entity) => (
                <div
                  key={entity.id}
                  className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border text-sm ${TYPE_COLORS[type] || 'bg-gray-800 text-gray-300 border-gray-600'}`}
                  title={entity.context}
                >
                  <span>{entity.name}</span>
                  {entity.confidence && (
                    <span className="text-[10px] opacity-60">
                      {Math.round(entity.confidence * 100)}%
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
