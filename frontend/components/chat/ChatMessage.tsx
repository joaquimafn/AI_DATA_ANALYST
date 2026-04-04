'use client'

import { Card, CardContent } from '@/components/ui/Card'
import type { ChatMessage as ChatMessageType } from '@/lib/types'

interface ChatMessageProps {
  message: ChatMessageType
}

function formatTimestamp(date: Date): string {
  return new Intl.DateTimeFormat('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user'
  const response = message.response

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[80%] ${isUser ? 'order-2' : 'order-1'}`}>
        <div className="flex items-center gap-2 mb-1">
          <span className={`text-sm font-medium ${isUser ? 'text-primary-600' : 'text-gray-600'}`}>
            {isUser ? 'Você' : 'AI Analyst'}
          </span>
          <span className="text-xs text-gray-400">
            {formatTimestamp(message.timestamp)}
          </span>
        </div>

        <Card variant={isUser ? 'elevated' : 'outlined'} className={isUser ? 'bg-primary-50' : ''}>
          <CardContent className="p-3">
            <p className="text-gray-800 font-medium mb-2">{message.question}</p>

            {response && !isUser && (
              <div className="mt-3 pt-3 border-t border-gray-200 space-y-3">
                {response.error ? (
                  <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-red-700 text-sm">{response.error}</p>
                  </div>
                ) : (
                  <>
                    {response.sql && (
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs font-semibold text-gray-500 uppercase">SQL</span>
                          {response.cached && (
                            <span className="text-xs px-2 py-0.5 bg-green-100 text-green-700 rounded">
                              cache
                            </span>
                          )}
                        </div>
                        <pre className="bg-gray-900 text-gray-100 p-3 rounded-lg text-sm overflow-x-auto">
                          <code>{response.sql}</code>
                        </pre>
                      </div>
                    )}

                    {response.explanation && (
                      <div>
                        <span className="text-xs font-semibold text-gray-500 uppercase">Explicação</span>
                        <p className="text-gray-600 text-sm mt-1">{response.explanation}</p>
                      </div>
                    )}

                    {response.data && response.data.length > 0 && (
                      <div>
                        <span className="text-xs font-semibold text-gray-500 uppercase">
                          Dados ({response.data.length} registros)
                        </span>
                        <div className="mt-2 overflow-x-auto">
                          <table className="w-full text-sm">
                            <thead>
                              <tr className="bg-gray-100">
                                {Object.keys(response.data[0]).map((key) => (
                                  <th key={key} className="px-3 py-2 text-left font-medium text-gray-600">
                                    {key}
                                  </th>
                                ))}
                              </tr>
                            </thead>
                            <tbody>
                              {response.data.slice(0, 5).map((row, idx) => (
                                <tr key={idx} className="border-t border-gray-100">
                                  {Object.values(row).map((val, i) => (
                                    <td key={i} className="px-3 py-2 text-gray-700">
                                      {String(val ?? '-')}
                                    </td>
                                  ))}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                          {response.data.length > 5 && (
                            <p className="text-xs text-gray-500 mt-2">
                              Mostrando 5 de {response.data.length} registros
                            </p>
                          )}
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
