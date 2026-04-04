'use client'

import { useState, useCallback } from 'react'
import { sendQuery, ApiError } from '@/lib/api'
import type { QueryRequest, QueryResponse, ChatMessage } from '@/lib/types'

interface UseNL2SQLReturn {
  messages: ChatMessage[]
  isLoading: boolean
  error: string | null
  sendQuestion: (question: string) => Promise<void>
  clearMessages: () => void
}

export function useNL2SQL(): UseNL2SQLReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const sendQuestion = useCallback(async (question: string) => {
    const messageId = crypto.randomUUID()
    
    const userMessage: ChatMessage = {
      id: messageId,
      role: 'user',
      question,
      response: null,
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)
    setError(null)

    try {
      const request: QueryRequest = { question }
      const response: QueryResponse = await sendQuery(request)

      const assistantMessage: ChatMessage = {
        id: messageId,
        role: 'assistant',
        question,
        response,
        timestamp: new Date(),
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (err) {
      const errorMessage = err instanceof ApiError 
        ? err.message 
        : 'Falha ao processar pergunta'
      setError(errorMessage)

      const errorAssistantMessage: ChatMessage = {
        id: messageId,
        role: 'assistant',
        question,
        response: {
          sql: '',
          explanation: '',
          data: null,
          chart_type: null,
          insight: null,
          cached: false,
          error: errorMessage,
        },
        timestamp: new Date(),
      }

      setMessages(prev => [...prev, errorAssistantMessage])
    } finally {
      setIsLoading(false)
    }
  }, [])

  const clearMessages = useCallback(() => {
    setMessages([])
    setError(null)
  }, [])

  return {
    messages,
    isLoading,
    error,
    sendQuestion,
    clearMessages,
  }
}
