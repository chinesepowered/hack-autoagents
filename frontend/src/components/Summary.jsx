import React from 'react'

export default function Summary({ text }) {
  if (!text) return null

  // Simple markdown-like rendering
  const lines = text.split('\n')

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-white mb-4">Intelligence Brief</h3>
      <div className="prose prose-invert prose-sm max-w-none space-y-2">
        {lines.map((line, i) => {
          if (line.startsWith('## ')) {
            return <h2 key={i} className="text-lg font-bold text-white mt-4 mb-2">{line.replace('## ', '')}</h2>
          }
          if (line.startsWith('### ')) {
            return <h3 key={i} className="text-md font-semibold text-primary-400 mt-3 mb-1">{line.replace('### ', '')}</h3>
          }
          if (line.startsWith('- ')) {
            return <li key={i} className="text-gray-300 ml-4 list-disc">{renderBold(line.replace('- ', ''))}</li>
          }
          if (line.startsWith('**')) {
            return <p key={i} className="text-gray-300">{renderBold(line)}</p>
          }
          if (line.trim() === '') return <div key={i} className="h-2" />
          return <p key={i} className="text-gray-400">{renderBold(line)}</p>
        })}
      </div>
    </div>
  )
}

function renderBold(text) {
  const parts = text.split(/(\*\*[^*]+\*\*)/)
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={i} className="text-white font-semibold">{part.slice(2, -2)}</strong>
    }
    return part
  })
}
