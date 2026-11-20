import { useEffect, useState } from 'react'
import { FindingAPI } from '../services/api'
import type { Finding } from '../types'

export default function Findings() {
  const [findings, setFindings] = useState<Finding[]>([])
  const [severity, setSeverity] = useState('')
  const [category, setCategory] = useState('')

  useEffect(() => {
    const params: Record<string, string> = {}
    if (severity) params.severity = severity
    if (category) params.category = category
    FindingAPI.list(params).then(setFindings).catch(console.error)
  }, [severity, category])

  return (
    <div>
      <h2>Findings</h2>
      <div className="filters">
        <select value={severity} onChange={(e) => setSeverity(e.target.value)}>
          <option value="">All Severities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
          <option value="informational">Informational</option>
        </select>
        <select value={category} onChange={(e) => setCategory(e.target.value)}>
          <option value="">All Categories</option>
          <option value="secrets">Secrets</option>
          <option value="dependency_vulnerability">Dependencies</option>
          <option value="sast">SAST</option>
          <option value="configuration">Configuration</option>
        </select>
      </div>
      {findings.length === 0 ? (
        <p>No findings found.</p>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Severity</th>
              <th>Category</th>
              <th>Title</th>
              <th>File</th>
              <th>Line</th>
            </tr>
          </thead>
          <tbody>
            {findings.map((f) => (
              <tr key={f.id}>
                <td><span className={`badge-${f.severity}`}>{f.severity}</span></td>
                <td>{f.category}</td>
                <td>{f.title}</td>
                <td>{f.affected_file || 'N/A'}</td>
                <td>{f.line_number || 'N/A'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
