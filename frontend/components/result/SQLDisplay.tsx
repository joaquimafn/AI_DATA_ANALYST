'use client'

import { useState } from 'react'
import { Card, CardContent } from '@/components/ui/Card'

interface SQLDisplayProps {
  sql: string
  cached?: boolean
  defaultExpanded?: boolean
}

const SQL_KEYWORDS = [
  'SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'NOT', 'IN', 'LIKE', 'BETWEEN',
  'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER', 'FULL', 'ON', 'AS',
  'ORDER', 'BY', 'ASC', 'DESC', 'LIMIT', 'OFFSET',
  'GROUP', 'HAVING', 'COUNT', 'SUM', 'AVG', 'MIN', 'MAX',
  'DISTINCT', 'WHERE', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END',
  'UNION', 'ALL', 'EXCEPT', 'INTERSECT',
  'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE',
]

const SQL_TYPES = [
  'VARCHAR', 'TEXT', 'INTEGER', 'BIGINT', 'SMALLINT', 'NUMERIC', 'DECIMAL',
  'REAL', 'DOUBLE', 'BOOLEAN', 'DATE', 'TIMESTAMP', 'TIMESTAMPTZ', 'TIME',
  'ARRAY', 'JSON', 'JSONB',
]

function highlightSQL(sql: string): string {
  let result = sql
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

  const keywordsPattern = new RegExp(`\\b(${SQL_KEYWORDS.join('|')})\\b`, 'gi')
  const typesPattern = new RegExp(`\\b(${SQL_TYPES.join('|')})\\b`, 'gi')
  const stringsPattern = /('(?:[^'\\]|\\.)*')/g
  const numbersPattern = /\b(\d+(?:\.\d+)?)\b/g
  const commentsPattern = /(--.*$)/gm

  result = result.replace(commentsPattern, '<span class="text-gray-500 italic">$1</span>')
  result = result.replace(stringsPattern, '<span class="text-green-600">$1</span>')
  result = result.replace(numbersPattern, '<span class="text-purple-600">$1</span>')
  result = result.replace(typesPattern, '<span class="text-blue-600 font-medium">$1</span>')
  result = result.replace(keywordsPattern, '<span class="text-blue-700 font-bold">$1</span>')

  return result
}

export function SQLDisplay({ sql, cached = false, defaultExpanded = true }: SQLDisplayProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded)
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(sql)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      console.error('Failed to copy')
    }
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center gap-2 text-sm font-semibold text-gray-500 uppercase hover:text-gray-700 transition-colors"
        >
          <span className={`transition-transform ${isExpanded ? 'rotate-90' : ''}`}>
            ›
          </span>
          SQL
        </button>
        {cached && (
          <span className="text-xs px-2 py-0.5 bg-green-100 text-green-700 rounded-full">
            cache
          </span>
        )}
        <button
          onClick={handleCopy}
          className="ml-auto text-xs px-2 py-1 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded transition-colors"
        >
          {copied ? '✓ Copiado' : 'Copiar'}
        </button>
      </div>

      {isExpanded && (
        <div className="relative group">
          <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg text-sm overflow-x-auto font-mono">
            <code dangerouslySetInnerHTML={{ __html: highlightSQL(sql) }} />
          </pre>
          <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              onClick={handleCopy}
              className="p-1.5 bg-gray-700 hover:bg-gray-600 rounded text-gray-300 text-xs"
              title="Copiar SQL"
            >
              {copied ? '✓' : '📋'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}