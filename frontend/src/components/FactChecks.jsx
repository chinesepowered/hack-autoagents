import React from 'react'

const VERDICT_CONFIG = {
  verified: { label: 'Verified', badge: 'badge-verified', icon: 'V' },
  disputed: { label: 'Disputed', badge: 'badge-disputed', icon: 'X' },
  context_needed: { label: 'Needs Context', badge: 'badge-context', icon: '~' },
  unverified: { label: 'Unverified', badge: 'badge-unverified', icon: '?' },
  error: { label: 'Error', badge: 'badge-disputed', icon: '!' },
}

export default function FactChecks({ checks }) {
  if (!checks.length) return null

  const verified = checks.filter((c) => c.verdict === 'verified').length
  const disputed = checks.filter((c) => c.verdict === 'disputed').length
  const context = checks.filter((c) => c.verdict === 'context_needed').length
  const unverified = checks.filter((c) => c.verdict === 'unverified').length

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Fact-Check Results</h3>
        <span className="text-xs text-gray-500">Powered by Yutori Research</span>
      </div>

      {/* Summary bar */}
      <div className="flex gap-4 mb-6">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-green-500" />
          <span className="text-sm text-gray-300">{verified} Verified</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-yellow-500" />
          <span className="text-sm text-gray-300">{context} Needs Context</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-red-500" />
          <span className="text-sm text-gray-300">{disputed} Disputed</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-gray-500" />
          <span className="text-sm text-gray-300">{unverified} Unverified</span>
        </div>
      </div>

      {/* Claims */}
      <div className="space-y-4">
        {checks.map((check) => {
          const config = VERDICT_CONFIG[check.verdict] || VERDICT_CONFIG.unverified
          let sources = []
          try {
            sources = JSON.parse(check.sources || '[]')
          } catch {}

          return (
            <div key={check.id} className="bg-gray-800/50 rounded-lg p-4 border border-gray-800">
              <div className="flex items-start gap-3">
                <div className={`shrink-0 mt-0.5 badge ${config.badge}`}>
                  {config.label}
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-white mb-2">
                    "{check.claim}"
                  </p>
                  <p className="text-xs text-gray-400 leading-relaxed">
                    {check.evidence}
                  </p>
                  {sources.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-2">
                      {sources.map((src, i) => (
                        <a
                          key={i}
                          href={src}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-[10px] text-primary-400 hover:text-primary-300 underline"
                        >
                          Source {i + 1}
                        </a>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
