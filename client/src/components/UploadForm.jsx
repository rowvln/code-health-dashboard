import { useState } from 'react'

export default function UploadForm({ onAnalyze, loading }) {
  const [selectedFile, setSelectedFile] = useState(null)

  function handleSubmit(event) {
    event.preventDefault()
    if (!selectedFile) return
    onAnalyze(selectedFile)
  }

  return (
    <form className="upload-form panel" onSubmit={handleSubmit}>
      <label htmlFor="fileUpload">Upload a Python file or zip archive</label>
      <input
        id="fileUpload"
        type="file"
        accept=".py,.zip"
        onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
      />
      <button type="submit" disabled={!selectedFile || loading}>
        {loading ? 'Analyzing...' : 'Analyze Code'}
      </button>
    </form>
  )
}
