const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

/**
 * Query the Agentic RAG system
 * @param {string} query - The user's question
 * @param {string} sessionId - Optional session ID
 * @returns {Promise<Object>} Response with answer, sources and agentic metadata
 */
export async function queryRAG(query, sessionId = null) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        query, 
        session_id: sessionId,
        stream: false 
      }),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
      throw new Error(error.detail || `HTTP error! status: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error('Error querying Agentic RAG:', error)
    throw error
  }
}

/**
 * Get system statistics and agent status
 * @returns {Promise<Object>} System metrics
 */
export async function getStats() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/stats`)

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error('Error fetching stats:', error)
    throw error
  }
}

/**
 * Check API health and agentic core status
 * @returns {Promise<Object>} Health status
 */
export async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`)
    return await response.json()
  } catch (error) {
    console.error('Error checking health:', error)
    throw error
  }
}

