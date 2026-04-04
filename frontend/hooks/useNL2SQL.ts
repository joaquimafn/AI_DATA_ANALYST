'use client'

import { useState, useCallback, useEffect } from 'react'
import { sendQuery, ApiError } from '@/lib/api'
import type { QueryRequest, QueryResponse, ChatMessage } from '@/lib/types'

const STORAGE_KEY = 'ai-data-analyst-history'
const MAX_HISTORY = 50

interface UseNL2SQLReturn {
  messages: ChatMessage[]
  isLoading: boolean
  error: string | null
  sendQuestion: (question: string) => Promise<void>
  clearMessages: () => void
  retryLastQuestion: () => Promise<void>
  historyQuestions: string[]
}

function loadHistory(): string[] {
  if (typeof window === 'undefined') return []
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    return stored ? JSON.parse(stored) : []
  } catch {
    return []
  }
}

function saveHistory(history: string[]) {
  if (typeof window === 'undefined') return
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(history.slice(0, MAX_HISTORY)))
  } catch {
    console.error('Failed to save history')
  }
}

export function useNL2SQL(): UseNL2SQLReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastQuestion, setLastQuestion] = useState<string | null>(null)
  const [historyQuestions, setHistoryQuestions] = useState<string[]>([])

  useEffect(() => {
    setHistoryQuestions(loadHistory())
  }, [])

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
    setLastQuestion(question)

    const newHistory = [question, ...loadHistory().filter(q => q !== question)].slice(0, MAX_HISTORY)
    saveHistory(newHistory)
    setHistoryQuestions(newHistory)

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

  const retryLastQuestion = useCallback(async () => {
    if (lastQuestion) {
      await sendQuestion(lastQuestion)
    }
  }, [lastQuestion, sendQuestion])

  const clearMessages = useCallback(() => {
    setMessages([])
    setError(null)
    setLastQuestion(null)
  }, [])

  return {
    messages,
    isLoading,
    error,
    sendQuestion,
    clearMessages,
    retryLastQuestion,
    historyQuestions,
  }
}