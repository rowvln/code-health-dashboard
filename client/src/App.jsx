/**
 * Main application component
 *
 * Responsibilities:
 * - handle file upload flow
 * - manage loading + error states
 * - render dashboard results
 *
 * Future improvement:
 * - add state management (e.g., context)
 * - support historical uploads
 */
import { useState } from 'react'
import UploadForm from './components/UploadForm'
import ScoreCard from './components/ScoreCard'
import FileTable from './components/FileTable'
import RecommendationList from './components/RecommendationList'
import IssuesList from './components/IssuesList'
import { analyzeFile } from './services/api'
import CollapsiblePanel from './components/CollapsiblePanel'

const initialResults = null

function getScoreSeverity(score) {
  if (score >= 90) return 'good'
  if (score >= 75) return 'fair'
  if (score >= 60) return 'warning'
  return 'danger'
}

function getIssueSeverity(issues) {
  if (issues === 0) return 'good'
  if (issues <= 5) return 'fair'
  if (issues <= 15) return 'warning'
  return 'danger'
}

function getComplexitySeverity(complexity) {
  if (complexity <= 5) return 'good'
  if (complexity <= 10) return 'fair'
  if (complexity <= 20) return 'warning'
  return 'danger'
}

export default function App() {
  const [results, setResults] = useState(initialResults)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [loadingMessage, setLoadingMessage] = useState('')

  async function handleAnalyze(file) {
    setLoading(true)
    setError('')
    setResults(null)

    const isZip = file.name.toLowerCase().endsWith('.zip')

    setLoadingMessage(
      isZip
        ? 'Uploading zip file and preparing analysis...'
        : 'Uploading Python file and preparing analysis...'
    )

    const phaseTwoTimer = setTimeout(() => {
      setLoadingMessage(
        isZip
          ? 'Analyzing multiple Python files... this may take a little longer for larger projects.'
          : 'Analyzing code quality and complexity...'
      )
    }, 1200)

    const phaseThreeTimer = setTimeout(() => {
      setLoadingMessage(
        isZip
          ? 'Still working... pylint and radon are reviewing the extracted files.'
          : 'Still working... reviewing lint findings and complexity.'
      )
    }, 5000)

    try {
      const data = await analyzeFile(file)
      setResults(data)
    } catch (err) {
      setError(err.message || 'Something went wrong while analyzing the file.')
    } finally {
      clearTimeout(phaseTwoTimer)
      clearTimeout(phaseThreeTimer)
      setLoading(false)
      setLoadingMessage('')
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

      {loading && (
        <section className="panel loading-panel">
          <div className="loading-row">
            <div className="spinner" />
            <div>
              <h2>Analyzing Code</h2>
              <p>{loadingMessage}</p>
              <small>
                Larger zip uploads may take longer because each Python file is reviewed individually.
              </small>
            </div>
          </div>
          <div className="loading-bar">
            <div className="loading-bar-fill" />
          </div>
        </section>
      )}

      {error && <div className="error-banner">{error}</div>}

      {results && (
        <main className="dashboard-grid">
          <ScoreCard
            title="Code Health Score"
            value={results.score}
            label={results.score_label}
            description="Overall score based on lint findings and code complexity."
            severity={getScoreSeverity(results.score)}
          />

          <ScoreCard
            title="Total Issues"
            value={results.summary.issues}
            label={results.summary.issues_label}
            description="Combined findings across all analyzed files."
            severity={getIssueSeverity(results.summary.issues)}
          />

          <ScoreCard
            title="Average Complexity"
            value={results.summary.complexity}
            label={results.summary.complexity_label}
            description="A higher number usually means the code is harder to understand, test, and maintain."
            severity={getComplexitySeverity(results.summary.complexity)}
          />

          <ScoreCard
            title="Files Analyzed"
            value={results.summary.files_analyzed}
            label={`${results.summary.high_severity} high-severity issue(s)`}
            description="Total Python files included in this scan."
            severity="neutral"
          />

          <CollapsiblePanel title="File Breakdown" defaultOpen={true}>
            <FileTable files={results.files} />
          </CollapsiblePanel>

          <CollapsiblePanel
            title="Issues Found"
            description="These are the specific findings detected during analysis. Reviewing them helps explain why the score and complexity landed where they did."
            defaultOpen={true}
          >
            <IssuesList issues={results.issues_found} />
          </CollapsiblePanel>

          <CollapsiblePanel
            title="Top Recommendations"
            description="These are the changes most likely to improve code health, reduce complexity, and make the code easier to maintain."
            defaultOpen={true}
          >
            <RecommendationList recommendations={results.recommendations} />
          </CollapsiblePanel>
        </main>
      )}
    </div>
  )
}