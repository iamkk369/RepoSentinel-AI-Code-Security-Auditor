import { useEffect, useState } from 'react'
import { RepoAPI, ScanAPI } from '../services/api'
import type { Repository } from '../types'

export default function Repositories() {
  const [repos, setRepos] = useState<Repository[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    RepoAPI.list().then((data) => { setRepos(data); setLoading(false) })
  }, [])

  const triggerScan = async (repoId: number) => {
    await ScanAPI.trigger(repoId)
    alert('Scan triggered!')
  }

  if (loading) return <div className="loading">Loading...</div>

  return (
    <div>
      <h2>Repositories</h2>
      {repos.length === 0 ? (
        <p>No repositories linked.</p>
      ) : (
        <table className="table">
          <thead>
            <tr><th>Name</th><th>Language</th><th>Visibility</th><th>Actions</th></tr>
          </thead>
          <tbody>
            {repos.map((r) => (
              <tr key={r.id}>
                <td>
                  <a href={r.html_url} target="_blank" rel="noreferrer">{r.full_name}</a>
                </td>
                <td>{r.language || 'N/A'}</td>
                <td>{r.visibility}</td>
                <td>
                  <button onClick={() => triggerScan(r.id)}>Scan</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
