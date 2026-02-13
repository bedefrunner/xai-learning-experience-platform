import { useState } from 'react'
import { lxpApiLogin } from '../generated/sdk.gen'
import { client } from '../generated/client.gen'

interface LoginProps {
  userType: 'student' | 'educator'
  onLoginSuccess: (user: {
    userId: number
    email: string
    firstName: string
    lastName: string
    userType: 'student' | 'educator'
    profileId: number
  }) => void
  onBack: () => void
}

export default function Login({ userType, onLoginSuccess, onBack }: LoginProps) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      // Configure API client
      client.setConfig({
        baseUrl: 'http://localhost:8000',
      })

      const response = await lxpApiLogin({
        body: {
          email,
          password,
          user_type: userType,
        },
      })

      if (response.error) {
        setError((response.error as any).detail || 'Login failed')
      } else if (response.data) {
        onLoginSuccess({
          userId: response.data.user_id,
          email: response.data.email,
          firstName: response.data.first_name,
          lastName: response.data.last_name,
          userType: response.data.user_type as 'student' | 'educator',
          profileId: response.data.profile_id,
        })
      }
    } catch (err) {
      setError('Network error. Please try again.')
      console.error('Login error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-container">
        <button className="back-button" onClick={onBack}>← Back</button>

        <h1>{userType === 'student' ? 'Student' : 'Teacher'} Login</h1>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="your.email@example.com"
              autoFocus
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="Enter your password"
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="login-button" disabled={loading}>
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <div className="demo-hint">
          <p><strong>Demo credentials:</strong></p>
          {userType === 'student' ? (
            <p>sarah.johnson@student.lxp.com / student123</p>
          ) : (
            <p>mr.smith@teacher.lxp.com / teacher123</p>
          )}
        </div>
      </div>
    </div>
  )
}
