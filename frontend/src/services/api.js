const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

/**
 * Query the RAG system
 * @param {string} query - The user's question
 * @param {number} k - Number of documents to retrieve (default: 5)
 * @returns {Promise<Object>} Response with answer and sources
 */
export async function queryRAG(query, k = 5) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query, k }),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
      throw new Error(error.detail || `HTTP error! status: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error('Error querying RAG:', error)
    throw error
  }
}

/**
 * Get system statistics
 * @returns {Promise<Object>} System statistics
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
 * Check API health
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

