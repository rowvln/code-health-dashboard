const API_BASE_URL = 'http://127.0.0.1:5000/api'

export async function analyzeFile(file) {
  const formData = new FormData()
  formData.append('file', file)

  let response

  try {
    response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      body: formData,
    })
  } catch (error) {
    throw new Error('Could not reach the backend. Make sure Flask is still running on port 5000.')
  }

  let data
  const contentType = response.headers.get('content-type') || ''

  if (contentType.includes('application/json')) {
    data = await response.json()
  } else {
    const text = await response.text()
    throw new Error(text || 'The backend returned a non-JSON response.')
  }

  if (!response.ok) {
    throw new Error(data.error || 'Failed to analyze file.')
  }

  return data
}