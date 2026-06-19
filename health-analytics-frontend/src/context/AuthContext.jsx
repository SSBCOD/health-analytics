import { createContext, useContext, useState, useEffect } from 'react'
import api from '../api/api'

const AuthContext = createContext()

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('health_token'))
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      fetchProfile()
    } else {
      setLoading(false)
    }
  }, [])

  const fetchProfile = async () => {
    try {
      const res = await api.get('/api/v1/auth/profile')
      setUser(res.data)
    } catch {
      clearAuth()
    } finally {
      setLoading(false)
    }
  }

  const clearAuth = () => {
    localStorage.removeItem('health_token')
    delete api.defaults.headers.common['Authorization']
    setToken(null)
    setUser(null)
  }

  const saveAuth = (data) => {
    const tok = data.access_token
    localStorage.setItem('health_token', tok)
    api.defaults.headers.common['Authorization'] = `Bearer ${tok}`
    setToken(tok)
    setUser({ id: data.user_id, email: data.email, full_name: data.full_name })
  }

  const login = async (email, password) => {
    const res = await api.post('/api/v1/auth/login', { email, password })
    saveAuth(res.data)
    return res.data
  }

  const register = async (email, password, full_name) => {
    const res = await api.post('/api/v1/auth/register', {
      email,
      password,
      full_name,
      preferred_language: 'kz',
    })
    saveAuth(res.data)
    return res.data
  }

  const logout = () => clearAuth()

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
