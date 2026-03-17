export default function ScoreCard({ title, value, label, description }) {
  return (
    <section className="panel score-card">
      <p className="card-label">{title}</p>
      <h2>{value}</h2>
      {label && <p className="card-status">{label}</p>}
      <p className="card-description">{description}</p>
    </section>
  )
}