export interface QueryRequest {
  question: string
  context?: Record<string, unknown>
}

export interface QueryResponse {
  sql: string
  explanation: string
  data: Record<string, unknown>[] | null
  chart_type: string | null
  insight: string | null
  cached: boolean
  error: string | null
}

export interface HealthResponse {
  status: 'healthy' | 'degraded'
  database: boolean
  redis: boolean
  version: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  question: string
  response: QueryResponse | null
  timestamp: Date
}
