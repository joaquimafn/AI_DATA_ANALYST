'use client'

import { useState, useMemo } from 'react'
import { Button } from '@/components/ui/Button'

interface DataTableProps {
  data: Record<string, unknown>[]
  pageSize?: number
}

type SortDirection = 'asc' | 'desc' | null

interface SortConfig {
  key: string
  direction: SortDirection
}

export function DataTable({ data, pageSize: initialPageSize = 10 }: DataTableProps) {
  const [pageSize, setPageSize] = useState(initialPageSize)
  const [currentPage, setCurrentPage] = useState(1)
  const [sortConfig, setSortConfig] = useState<SortConfig | null>(null)

  const sortedData = useMemo(() => {
    if (!sortConfig || !sortConfig.direction) return data

    return [...data].sort((a, b) => {
      const aVal = a[sortConfig.key]
      const bVal = b[sortConfig.key]

      if (aVal === null || aVal === undefined) return 1
      if (bVal === null || bVal === undefined) return -1

      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortConfig.direction === 'asc' ? aVal - bVal : bVal - aVal
      }

      const aStr = String(aVal).toLowerCase()
      const bStr = String(bVal).toLowerCase()
      return sortConfig.direction === 'asc'
        ? aStr.localeCompare(bStr)
        : bStr.localeCompare(aStr)
    })
  }, [data, sortConfig])

  const totalPages = Math.ceil(sortedData.length / pageSize)
  const startIndex = (currentPage - 1) * pageSize
  const endIndex = startIndex + pageSize
  const paginatedData = sortedData.slice(startIndex, endIndex)

  const handleSort = (key: string) => {
    setSortConfig(prev => {
      if (prev?.key !== key) return { key, direction: 'asc' }
      if (prev.direction === 'asc') return { key, direction: 'desc' }
      return null
    })
    setCurrentPage(1)
  }

  const handlePageSizeChange = (newSize: number) => {
    setPageSize(newSize)
    setCurrentPage(1)
  }

  const getSortIndicator = (key: string) => {
    if (sortConfig?.key !== key) return '↕'
    return sortConfig.direction === 'asc' ? '↑' : '↓'
  }

  if (data.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        Nenhum dado encontrado
      </div>
    )
  }

  const columns = Object.keys(data[0])

  return (
    <div className="space-y-4">
      <div className="overflow-x-auto border border-gray-200 rounded-lg">
        <table className="w-full text-sm">
          <thead className="bg-gray-50">
            <tr>
              {columns.map(col => (
                <th
                  key={col}
                  onClick={() => handleSort(col)}
                  className="px-4 py-3 text-left font-medium text-gray-600 cursor-pointer hover:bg-gray-100 transition-colors"
                >
                  <span className="flex items-center gap-1">
                    {col}
                    <span className="text-gray-400 text-xs">{getSortIndicator(col)}</span>
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paginatedData.map((row, idx) => (
              <tr
                key={idx}
                className="border-t border-gray-100 hover:bg-gray-50 transition-colors"
              >
                {columns.map(col => (
                  <td key={col} className="px-4 py-2 text-gray-700">
                    {row[col] === null || row[col] === undefined
                      ? <span className="text-gray-400">-</span>
                      : String(row[col])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between text-sm text-gray-600">
        <div className="flex items-center gap-2">
          <span>Linhas por página:</span>
          <select
            value={pageSize}
            onChange={e => handlePageSizeChange(Number(e.target.value))}
            className="border border-gray-300 rounded px-2 py-1 bg-white"
          >
            <option value={10}>10</option>
            <option value={25}>25</option>
            <option value={50}>50</option>
          </select>
        </div>

        <div className="flex items-center gap-2">
          <span>
            {startIndex + 1}-{Math.min(endIndex, sortedData.length)} de {sortedData.length}
          </span>
          <div className="flex gap-1">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
            >
              ‹
            </Button>
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              let page: number
              if (totalPages <= 5) {
                page = i + 1
              } else if (currentPage <= 3) {
                page = i + 1
              } else if (currentPage >= totalPages - 2) {
                page = totalPages - 4 + i
              } else {
                page = currentPage - 2 + i
              }
              return (
                <Button
                  key={page}
                  variant={currentPage === page ? 'primary' : 'secondary'}
                  size="sm"
                  onClick={() => setCurrentPage(page)}
                >
                  {page}
                </Button>
              )
            })}
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
            >
              ›
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}