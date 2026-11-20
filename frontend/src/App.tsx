import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Repositories from './pages/Repositories'
import ScanDetails from './pages/ScanDetails'
import Findings from './pages/Findings'

function App() {
  const token = localStorage.getItem('token')

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/auth/callback" element={<Login />} />
      <Route element={token ? <Layout /> : <Navigate to="/login" />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/repositories" element={<Repositories />} />
        <Route path="/scans/:scanId" element={<ScanDetails />} />
        <Route path="/findings" element={<Findings />} />
      </Route>
    </Routes>
  )
}

export default App
