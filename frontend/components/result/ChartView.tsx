'use client'

import { useMemo, useState } from 'react'
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

type ChartType = 'bar' | 'line' | 'pie'

interface ChartViewProps {
  data: Record<string, unknown>[]
  suggestedType?: string | null
}

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16']

function detectDataType(values: unknown[]): 'temporal' | 'categorical' | 'numeric' {
  const sample = values.slice(0, 20).filter(v => v !== null && v !== undefined)
  
  const datePatterns = [
    /^\d{4}-\d{2}-\d{2}/,
    /^\d{2}\/\d{2}\/\d{4}/,
    /^\d{4}-\d{2}/,
  ]

  for (const val of sample) {
    const str = String(val)
    if (datePatterns.some(p => p.test(str))) return 'temporal'
  }

  const numericCount = sample.filter(v => !isNaN(Number(v))).length
  if (numericCount / sample.length > 0.7) return 'numeric'

  return 'categorical'
}

function suggestChartType(data: Record<string, unknown>[]): ChartType {
  if (data.length === 0) return 'bar'

  const columns = Object.keys(data[0])
  const numericColumns = columns.filter(col => {
    const values = data.map(row => row[col])
    const numericCount = values.filter(v => !isNaN(Number(v))).length
    return numericCount / values.length > 0.5
  })

  if (numericColumns.length === 0) return 'bar'

  const categoricalColumns = columns.filter(col => {
    if (numericColumns.includes(col)) return false
    const uniqueValues = new Set(data.map(row => row[col]))
    return uniqueValues.size <= 20
  })

  if (categoricalColumns.length > 0) {
    const firstCatCol = categoricalColumns[0]
    const uniqueCount = new Set(data.map(row => row[firstCatCol])).size
    
    if (uniqueCount <= 6) return 'pie'
    return 'bar'
  }

  return 'line'
}

function getChartConfig(data: Record<string, unknown>[], chartType: ChartType) {
  const columns = Object.keys(data[0])
  
  const numericColumns = columns.filter(col => {
    const values = data.map(row => row[col])
    return values.filter(v => !isNaN(Number(v))).length / values.length > 0.5
  })

  const categoricalColumns = columns.filter(col => !numericColumns.includes(col))

  let xAxis = categoricalColumns[0] || columns[0]
  let yAxis = numericColumns[0] || columns[1] || columns[0]
  let pieIndex = categoricalColumns[0] || columns[0]
  let pieValue = numericColumns[0] || columns[1] || columns[0]

  return { xAxis, yAxis, pieIndex, pieValue, categoricalColumns, numericColumns }
}

export function ChartView({ data, suggestedType }: ChartViewProps) {
  const [chartType, setChartType] = useState<ChartType>(() => {
    if (suggestedType && ['bar', 'line', 'pie'].includes(suggestedType)) {
      return suggestedType as ChartType
    }
    return suggestChartType(data)
  })

  const chartConfig = useMemo(() => getChartConfig(data, chartType), [data, chartType])

  const { xAxis, yAxis, pieIndex, pieValue } = chartConfig

  const pieData = useMemo(() => {
    const grouped: Record<string, number> = {}
    data.forEach(row => {
      const key = String(row[pieIndex] ?? 'N/A')
      const val = Number(row[pieValue]) || 0
      grouped[key] = (grouped[key] || 0) + val
    })
    return Object.entries(grouped).map(([name, value]) => ({ name, value }))
  }, [data, pieIndex, pieValue])

  if (!data || data.length === 0) return null

  const renderChart = () => {
    switch (chartType) {
      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis
                dataKey={xAxis}
                tick={{ fill: '#6B7280', fontSize: 12 }}
                angle={-45}
                textAnchor="end"
                height={60}
              />
              <YAxis tick={{ fill: '#6B7280', fontSize: 12 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #E5E7EB',
                  borderRadius: '8px',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                }}
              />
              <Legend />
              <Bar
                dataKey={yAxis}
                fill="#3B82F6"
                radius={[4, 4, 0, 0]}
                name={String(yAxis)}
                animationDuration={500}
              />
            </BarChart>
          </ResponsiveContainer>
        )

      case 'line':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis
                dataKey={xAxis}
                tick={{ fill: '#6B7280', fontSize: 12 }}
                angle={-45}
                textAnchor="end"
                height={60}
              />
              <YAxis tick={{ fill: '#6B7280', fontSize: 12 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #E5E7EB',
                  borderRadius: '8px',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey={yAxis}
                stroke="#10B981"
                strokeWidth={2}
                dot={{ fill: '#10B981', strokeWidth: 2 }}
                name={String(yAxis)}
                animationDuration={500}
              />
            </LineChart>
          </ResponsiveContainer>
        )

      case 'pie':
        return (
          <div className="flex items-center justify-center gap-8">
            <ResponsiveContainer width="60%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  innerRadius={50}
                  paddingAngle={2}
                  dataKey="value"
                  animationDuration={500}
                  label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                >
                  {pieData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex flex-col gap-2">
              {pieData.map((entry, index) => (
                <div key={entry.name} className="flex items-center gap-2 text-sm">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: COLORS[index % COLORS.length] }}
                  />
                  <span className="text-gray-600">{entry.name}</span>
                </div>
              ))}
            </div>
          </div>
        )
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-gray-500 uppercase">
          Visualização ({data.length} registros)
        </span>
        <div className="flex gap-1">
          {(['bar', 'line', 'pie'] as ChartType[]).map(type => (
            <button
              key={type}
              onClick={() => setChartType(type)}
              className={`px-3 py-1 text-xs rounded-full transition-colors ${
                chartType === type
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {type === 'bar' && 'Barras'}
              {type === 'line' && 'Linha'}
              {type === 'pie' && 'Pizza'}
            </button>
          ))}
        </div>
      </div>

      <div className="border border-gray-200 rounded-lg p-4 bg-white">
        {renderChart()}
      </div>
    </div>
  )
}