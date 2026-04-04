import type { QueryRequest, QueryResponse, HealthResponse } from './types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new ApiError(
      errorData.error || 'Request failed',
      response.status,
      errorData.code
    )
  }
  return response.json()
}

export async function sendQuery(request: QueryRequest): Promise<QueryResponse> {
  const response = await fetch(`${API_URL}/api/v1/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  })

  return handleResponse<QueryResponse>(response)
}

export async function checkHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_URL}/health`)
  return handleResponse<HealthResponse>(response)
}

export { ApiError }
