import { useState } from 'react'

export default function UploadForm({ onAnalyze, loading }) {
  const [selectedFile, setSelectedFile] = useState(null)

  function handleSubmit(event) {
    event.preventDefault()

    if (!selectedFile || loading) {
      return
    }

    onAnalyze(selectedFile)
  }

  function handleFileChange(event) {
    const file = event.target.files?.[0] || null
    setSelectedFile(file)
  }

  return (
    <form className="panel upload-form" onSubmit={handleSubmit}>
      <label htmlFor="file-upload">Upload a Python file or zipped project</label>
      <input
        id="file-upload"
        type="file"
        accept=".py,.zip"
        onChange={handleFileChange}
        disabled={loading}
      />
      <button type="submit" disabled={!selectedFile || loading}>
        {loading ? 'Analyzing...' : 'Analyze Code'}
      </button>
    </form>
  )
}