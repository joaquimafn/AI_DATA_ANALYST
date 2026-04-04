'use client'

import { useNL2SQL } from '@/hooks/useNL2SQL'
import { ChatInput } from '@/components/chat/ChatInput'
import { ChatMessage } from '@/components/chat/ChatMessage'
import { MessageSkeleton } from '@/components/state'

function Header() {
  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
      <div className="max-w-4xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">AI Data Analyst</h1>
            <p className="text-sm text-gray-500">Pergunte sobre seus dados em linguagem natural</p>
          </div>
          <div className="flex items-center gap-2">
            <span className="flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-3 w-3 rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
            </span>
            <span className="text-sm text-gray-600">Online</span>
          </div>
        </div>
      </div>
    </header>
  )
}

function EmptyState({ onSuggestionClick }: { onSuggestionClick: (q: string) => void }) {
  const suggestions = [
    'Quais são os 10 produtos mais vendidos?',
    'Qual o faturamento por região no último mês?',
    'Quantos clientes fizeram compras esta semana?',
  ]

  return (
    <div className="flex-1 flex items-center justify-center">
      <div className="text-center max-w-md px-4">
        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-primary-100 flex items-center justify-center">
          <svg
            className="w-8 h-8 text-primary-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
            />
          </svg>
        </div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          Como posso ajudar?
        </h2>
        <p className="text-gray-500">
          Faça uma pergunta sobre seus dados e eu vou gerar a query SQL, 
          executar e retornar os resultados com insights.
        </p>
        <div className="mt-6 space-y-2 text-left">
          <p className="text-sm font-medium text-gray-700">Exemplos:</p>
          <ul className="text-sm text-gray-600 space-y-1">
            {suggestions.map((suggestion, i) => (
              <li key={i}>
                <button
                  onClick={() => onSuggestionClick(suggestion)}
                  className="text-left hover:text-primary-600 transition-colors"
                >
                  • {suggestion}
                </button>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}

function HistoryPanel({
  history,
  onSelect,
}: {
  history: string[]
  onSelect: (q: string) => void
}) {
  if (history.length === 0) return null

  return (
    <div className="bg-white border-b border-gray-200 px-4 py-3">
      <p className="text-xs font-medium text-gray-500 uppercase mb-2">Histórico</p>
      <div className="flex gap-2 overflow-x-auto pb-1">
        {history.slice(0, 5).map((q, i) => (
          <button
            key={i}
            onClick={() => onSelect(q)}
            className="text-xs px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-600 whitespace-nowrap transition-colors"
          >
            {q.length > 40 ? q.slice(0, 40) + '...' : q}
          </button>
        ))}
      </div>
    </div>
  )
}

export default function Home() {
  const {
    messages,
    isLoading,
    error,
    sendQuestion,
    clearMessages,
    retryLastQuestion,
    historyQuestions,
  } = useNL2SQL()

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header />

      {historyQuestions.length > 0 && messages.length === 0 && (
        <HistoryPanel history={historyQuestions} onSelect={sendQuestion} />
      )}

      <main className="flex-1 max-w-4xl mx-auto w-full px-4 py-6 flex flex-col">
        {messages.length === 0 && !isLoading ? (
          <EmptyState onSuggestionClick={sendQuestion} />
        ) : (
          <div className="flex-1 overflow-y-auto space-y-4 pb-4">
            {messages.map((message) => (
              <ChatMessage
                key={message.id}
                message={message}
                onRetry={retryLastQuestion}
              />
            ))}
            {isLoading && <MessageSkeleton />}
          </div>
        )}

        {error && !isLoading && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg animate-in fade-in duration-200">
            <p className="text-red-700 text-sm mb-2">{error}</p>
            <button
              onClick={retryLastQuestion}
              className="text-xs text-red-600 hover:text-red-800 font-medium underline"
            >
              Tentar novamente
            </button>
          </div>
        )}

        <div className="bg-white border-t border-gray-200 -mx-4 px-4 py-4 sticky bottom-0 shadow-lg">
          <ChatInput
            onSend={sendQuestion}
            isLoading={isLoading}
          />
          {messages.length > 0 && (
            <div className="mt-3 flex justify-center gap-4">
              <button
                onClick={clearMessages}
                className="text-sm text-gray-500 hover:text-gray-700 transition-colors"
              >
                Limpar conversa
              </button>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}