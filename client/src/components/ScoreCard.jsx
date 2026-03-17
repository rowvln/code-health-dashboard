/**
 * ScoreCard
 *
 * Displays a key metric with:
 * - numeric value
 * - severity badge
 * - descriptive label
 *
 * Used for:
 * - high-level dashboard insights
 *
 * Design:
 * - prioritizes quick visual scanning
 * - separates raw value from interpretation
 */
export default function ScoreCard({ title, value, label, description, severity = 'neutral' }) {
  return (
    <section className="panel score-card">
      <p className="card-label">{title}</p>

      <div className="card-value-row">
        <h2>{value}</h2>
        <span className={`status-badge status-${severity}`}>
          {severity === 'good' && 'Good'}
          {severity === 'fair' && 'Fair'}
          {severity === 'warning' && 'Attention'}
          {severity === 'danger' && 'High Risk'}
          {severity === 'neutral' && 'Info'}
        </span>
      </div>

      {label && <p className="card-status-text">{label}</p>}
      <p className="card-description">{description}</p>
    </section>
  )
}