'use client'

import { useState, FormEvent } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'

interface ChatInputProps {
  onSend: (question: string) => void
  isLoading: boolean
  disabled?: boolean
}

export function ChatInput({ onSend, isLoading, disabled }: ChatInputProps) {
  const [question, setQuestion] = useState('')

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    const trimmedQuestion = question.trim()
    if (!trimmedQuestion || isLoading) return

    onSend(trimmedQuestion)
    setQuestion('')
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <div className="flex-1">
        <Input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Faça uma pergunta sobre seus dados..."
          disabled={disabled || isLoading}
          className="w-full"
        />
      </div>
      <Button
        type="submit"
        disabled={!question.trim() || isLoading}
        className="px-6"
      >
        {isLoading ? (
          <span className="flex items-center gap-2">
            <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
                fill="none"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            Enviando
          </span>
        ) : (
          'Enviar'
        )}
      </Button>
    </form>
  )
}
