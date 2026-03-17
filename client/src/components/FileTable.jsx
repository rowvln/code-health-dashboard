export default function FileTable({ files }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>File</th>
            <th>Score</th>
            <th>Issues</th>
            <th>Complexity</th>
          </tr>
        </thead>
        <tbody>
          {files.map((file) => (
            <tr key={file.name}>
              <td>{file.name}</td>
              <td>
                <div className="metric-value">{file.score}</div>
                <div className="metric-label">{file.score_label}</div>
              </td>
              <td>
                <div className="metric-value">{file.issues}</div>
                <div className="metric-label">{file.issues_label}</div>
              </td>
              <td>
                <div className="metric-value">{file.complexity}</div>
                <div className="metric-label">{file.complexity_label}</div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}