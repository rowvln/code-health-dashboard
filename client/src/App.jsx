import { useState } from 'react'
import UploadForm from './components/UploadForm'
import ScoreCard from './components/ScoreCard'
import FileTable from './components/FileTable'
import RecommendationList from './components/RecommendationList'
import IssuesList from './components/IssuesList'
import { analyzeFile } from './services/api'

const initialResults = null

export default function App() {
  const [results, setResults] = useState(initialResults)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleAnalyze(file) {
    setLoading(true)
    setError('')

    try {
      const data = await analyzeFile(file)
      setResults(data)
    } catch (err) {
      setError(err.message || 'Something went wrong while analyzing the file.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-shell">
      <header className="hero">
        <p className="eyebrow">Portfolio MVP</p>
        <h1>Code Health Dashboard</h1>
        <p className="subtitle">
          Translate code quality signals into simple insights that both technical and non-technical users can understand.
        </p>
      </header>

      <UploadForm onAnalyze={handleAnalyze} loading={loading} />

      {error && <div className="error-banner">{error}</div>}

      {results && (
        <main className="dashboard-grid">
          <ScoreCard
            title="Code Health Score"
            value={results.score}
            label={results.score_label}
            description="Overall score based on lint findings and code complexity."
          />

          <ScoreCard
            title="Total Issues"
            value={results.summary.issues}
            label={results.summary.issues_label}
            description="Combined findings across all analyzed files."
          />

          <ScoreCard
            title="Average Complexity"
            value={results.summary.complexity}
            label={results.summary.complexity_label}
            description="A higher number usually means the code is harder to understand, test, and maintain."
          />

          <ScoreCard
            title="Files Analyzed"
            value={results.summary.files_analyzed}
            label={`${results.summary.high_severity} high-severity issue(s)`}
            description="Total Python files included in this scan."
          />

          <section className="panel panel-wide">
            <h2>File Breakdown</h2>
            <FileTable files={results.files} />
          </section>

          <section className="panel panel-wide">
            <h2>Issues Found</h2>
            <p className="section-description">
              These are the specific findings detected during analysis. Reviewing them helps explain why the score and complexity landed where they did.
            </p>
            <IssuesList issues={results.issues_found} />
          </section>

          <section className="panel panel-wide">
            <h2>Top Recommendations</h2>
            <p className="section-description">
              These are the 3–5 changes most likely to improve code health, reduce complexity, and make the code easier to maintain.
            </p>
            <RecommendationList recommendations={results.recommendations} />
          </section>
        </main>
      )}
    </div>
  )
}