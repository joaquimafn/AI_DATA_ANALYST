'use client'

import { useState } from 'react'
import { Card, CardContent } from '@/components/ui/Card'
import { SQLDisplay } from './SQLDisplay'
import { DataTable } from './DataTable'
import { ChartView } from './ChartView'
import { InsightCard } from './InsightCard'

interface ResultCardProps {
  sql: string
  explanation: string
  data: Record<string, unknown>[] | null
  chartType?: string | null
  insight?: string | null
  cached?: boolean
}

type ViewMode = 'table' | 'chart' | 'both'

export function ResultCard({
  sql,
  explanation,
  data,
  chartType,
  insight,
  cached = false,
}: ResultCardProps) {
  const [viewMode, setViewMode] = useState<ViewMode>(
    data && data.length > 0 ? 'both' : 'table'
  )

  return (
    <div className="space-y-4">
      <SQLDisplay sql={sql} cached={cached} />

      {explanation && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <span className="text-xs font-semibold text-blue-600 uppercase">Explicação</span>
          <p className="text-sm text-blue-800 mt-1">{explanation}</p>
        </div>
      )}

      {insight && <InsightCard insight={insight} />}

      {data && data.length > 0 && (
        <>
          <div className="flex items-center gap-2 border-b border-gray-200 pb-2">
            <span className="text-xs font-semibold text-gray-500 uppercase">
              Dados ({data.length} registros)
            </span>
            <div className="ml-auto flex gap-1">
              <button
                onClick={() => setViewMode('table')}
                className={`px-3 py-1 text-xs rounded-full transition-colors ${
                  viewMode === 'table'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                Tabela
              </button>
              <button
                onClick={() => setViewMode('chart')}
                className={`px-3 py-1 text-xs rounded-full transition-colors ${
                  viewMode === 'chart'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                Gráfico
              </button>
              <button
                onClick={() => setViewMode('both')}
                className={`px-3 py-1 text-xs rounded-full transition-colors ${
                  viewMode === 'both'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                Ambos
              </button>
            </div>
          </div>

          {viewMode !== 'chart' && (
            <div className={viewMode === 'both' ? 'border-b border-gray-200 pb-4 mb-4' : ''}>
              <DataTable data={data} pageSize={10} />
            </div>
          )}

          {viewMode !== 'table' && (
            <ChartView data={data} suggestedType={chartType} />
          )}
        </>
      )}
    </div>
  )
}