'use client'

import { useState } from 'react'

interface InsightCardProps {
  insight: string
}

export function InsightCard({ insight }: InsightCardProps) {
  const [isExpanded, setIsExpanded] = useState(true)

  return (
    <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-4">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center gap-2 text-left"
      >
        <svg
          className="w-5 h-5 text-purple-600 flex-shrink-0"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"
          />
        </svg>
        <span className="text-xs font-semibold text-purple-700 uppercase">
          Insight
        </span>
        <span className={`ml-auto transition-transform ${isExpanded ? 'rotate-180' : ''}`}>
          ›
        </span>
      </button>

      {isExpanded && (
        <p className="text-sm text-gray-700 mt-2 leading-relaxed">
          {insight}
        </p>
      )}
    </div>
  )
}