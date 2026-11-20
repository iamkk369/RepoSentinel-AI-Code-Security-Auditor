import { useEffect, useState } from 'react'
import { DashboardAPI } from '../services/api'

export default function Dashboard() {
  const [metrics, setMetrics] = useState<any>(null)

  useEffect(() => {
    DashboardAPI.metrics().then(setMetrics).catch(console.error)
  }, [])

  if (!metrics) return <div className="loading">Loading...</div>

  return (
    <div className="dashboard">
      <h2>Dashboard</h2>
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{metrics.total_repositories ?? 0}</div>
          <div className="stat-label">Repositories</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{metrics.total_scans ?? 0}</div>
          <div className="stat-label">Scans</div>
        </div>
        <div className="stat-card critical">
          <div className="stat-value">{metrics.severity_distribution?.critical ?? 0}</div>
          <div className="stat-label">Critical</div>
        </div>
        <div className="stat-card high">
          <div className="stat-value">{metrics.severity_distribution?.high ?? 0}</div>
          <div className="stat-label">High</div>
        </div>
        <div className="stat-card medium">
          <div className="stat-value">{metrics.severity_distribution?.medium ?? 0}</div>
          <div className="stat-label">Medium</div>
        </div>
        <div className="stat-card low">
          <div className="stat-value">{metrics.severity_distribution?.low ?? 0}</div>
          <div className="stat-label">Low</div>
        </div>
      </div>

      <h3>Recent Scans</h3>
      {metrics.recent_scans?.length ? (
        <table className="table">
          <thead>
            <tr><th>Scan ID</th><th>Status</th><th>Findings</th></tr>
          </thead>
          <tbody>
            {metrics.recent_scans.map((s: any) => (
              <tr key={s.id}>
                <td>{s.id}</td>
                <td className={`status-${s.status}`}>{s.status}</td>
                <td>{s.total_findings}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p>No scans yet.</p>
      )}
    </div>
  )
}
