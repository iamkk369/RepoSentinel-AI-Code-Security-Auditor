import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { ScanAPI } from '../services/api'

export default function ScanDetails() {
  const { scanId } = useParams()
  const [scan, setScan] = useState<any>(null)

  useEffect(() => {
    if (scanId) {
      ScanAPI.get(Number(scanId)).then(setScan).catch(console.error)
    }
  }, [scanId])

  if (!scan) return <div className="loading">Loading...</div>

  return (
    <div>
      <h2>Scan #{scan.id}</h2>
      <p>Status: <span className={`status-${scan.status}`}>{scan.status}</span></p>
      <p>Branch: {scan.branch}</p>
      <p>Date: {new Date(scan.created_at).toLocaleString()}</p>
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{scan.total_findings}</div>
          <div className="stat-label">Total</div>
        </div>
        <div className="stat-card critical">
          <div className="stat-value">{scan.critical_count}</div>
          <div className="stat-label">Critical</div>
        </div>
        <div className="stat-card high">
          <div className="stat-value">{scan.high_count}</div>
          <div className="stat-label">High</div>
        </div>
        <div className="stat-card medium">
          <div className="stat-value">{scan.medium_count}</div>
          <div className="stat-label">Medium</div>
        </div>
      </div>
      {scan.error_message && <p className="error">Error: {scan.error_message}</p>}
    </div>
  )
}
