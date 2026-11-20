import { useEffect } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { AuthAPI } from '../services/api'

export default function Login() {
  const [params] = useSearchParams()
  const navigate = useNavigate()

  useEffect(() => {
    const code = params.get('code')
    if (code) {
      AuthAPI.callback(code).then((data) => {
        localStorage.setItem('token', data.access_token)
        navigate('/')
      }).catch(() => {
        alert('Login failed')
      })
    }
  }, [params, navigate])

  const startLogin = async () => {
    const data = await AuthAPI.loginUrl()
    window.location.href = data.auth_url
  }

  return (
    <div className="login-container">
      <h1>RepoSentinel</h1>
      <p>AI-Assisted GitHub Repository Security Intelligence</p>
      <button onClick={startLogin}>Sign in with GitHub</button>
    </div>
  )
}
