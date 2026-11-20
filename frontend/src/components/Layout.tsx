import { Outlet, Link, useNavigate } from 'react-router-dom'

export default function Layout() {
  const navigate = useNavigate()

  const logout = () => {
    localStorage.removeItem('token')
    navigate('/login')
  }

  return (
    <div className="layout">
      <nav className="sidebar">
        <div className="brand">RepoSentinel</div>
        <Link to="/">Dashboard</Link>
        <Link to="/repositories">Repositories</Link>
        <Link to="/findings">Findings</Link>
        <button className="logout" onClick={logout}>Logout</button>
      </nav>
      <main className="content">
        <Outlet />
      </main>
    </div>
  )
}
