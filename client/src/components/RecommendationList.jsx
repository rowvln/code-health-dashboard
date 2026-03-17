export default function RecommendationList({ recommendations }) {
  return (
    <ul className="recommendation-list">
      {recommendations.map((item) => (
        <li key={item}>{item}</li>
      ))}
    </ul>
  )
}
