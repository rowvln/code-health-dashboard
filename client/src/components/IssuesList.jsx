export default function IssuesList({ issues }) {
  if (!issues || issues.length === 0) {
    return <p className="empty-state">No issues found.</p>
  }

  return (
    <div className="issues-list">
      {issues.map((issue, index) => (
        <div className="issue-item" key={`${issue.file}-${issue.line}-${issue.message}-${index}`}>
          <p className="issue-title">
            <strong>{issue.file}</strong> · line {issue.line}
          </p>
          <p className="issue-meta">
            <span className={`issue-badge issue-${issue.type}`}>{issue.type}</span>
          </p>
          <p className="issue-message">{issue.message}</p>
        </div>
      ))}
    </div>
  )
}