'use client'

import { useState } from 'react'
import { Card, CardContent } from '@/components/ui/Card'
import { ResultCard } from '@/components/result'
import { ErrorState } from '@/components/state'
import type { ChatMessage as ChatMessageType } from '@/lib/types'

interface ChatMessageProps {
  message: ChatMessageType
  onRetry?: () => void
}

function formatTimestamp(date: Date): string {
  return new Intl.DateTimeFormat('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

export function ChatMessage({ message, onRetry }: ChatMessageProps) {
  const isUser = message.role === 'user'
  const response = message.response

  return (
    <div
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2 duration-300`}
    >
      <div className={`max-w-[85%] ${isUser ? 'order-2' : 'order-1'}`}>
        <div className="flex items-center gap-2 mb-1">
          <span className={`text-sm font-medium ${isUser ? 'text-primary-600' : 'text-gray-600'}`}>
            {isUser ? 'Você' : 'AI Analyst'}
          </span>
          <span className="text-xs text-gray-400">
            {formatTimestamp(message.timestamp)}
          </span>
          {!isUser && response?.cached && (
            <span className="text-xs px-2 py-0.5 bg-green-100 text-green-700 rounded-full">
              cache
            </span>
          )}
        </div>

        <Card
          variant={isUser ? 'elevated' : 'outlined'}
          className={`${isUser ? 'bg-primary-50' : ''} transition-all duration-200 hover:shadow-md`}
        >
          <CardContent className="p-4">
            <p className="text-gray-800 font-medium mb-2">{message.question}</p>

            {response && !isUser && (
              <div className="mt-3 pt-3 border-t border-gray-200">
                {response.error ? (
                  <ErrorState message={response.error} onRetry={onRetry} />
                ) : (
                  <ResultCard
                    sql={response.sql}
                    explanation={response.explanation}
                    data={response.data}
                    chartType={response.chart_type}
                    insight={response.insight}
                    cached={response.cached}
                  />
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}