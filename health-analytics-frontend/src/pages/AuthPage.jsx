import { useState } from 'react'
import { useNavigate, Navigate } from 'react-router-dom'
import { Activity, Mail, Lock, User, AlertCircle } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { useLang } from '../context/LangContext'

export default function AuthPage() {
  const { login, register, token } = useAuth()
  const { t } = useLang()
  const navigate = useNavigate()

  const [mode, setMode] = useState('login')
  const [form, setForm] = useState({ email: '', password: '', full_name: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  if (token) return <Navigate to="/analyze" replace />

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      if (mode === 'login') {
        await login(form.email, form.password)
      } else {
        await register(form.email, form.password, form.full_name)
      }
      navigate('/analyze')
    } catch (err) {
      setError(err.response?.data?.detail || t('error_generic'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen pt-16 flex items-center justify-center px-4 bg-gradient-to-br from-warm-50 to-health-50/20">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-14 h-14 bg-gradient-to-br from-health-500 to-health-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-md">
            <Activity size={26} className="text-white" />
          </div>
          <h1 className="font-display text-2xl font-semibold text-warm-900">Health Analytics</h1>
        </div>

        <div className="card">
          {/* Tabs */}
          <div className="flex bg-warm-100 rounded-xl p-1 mb-6">
            {['login', 'register'].map((m) => (
              <button
                key={m}
                onClick={() => { setMode(m); setError('') }}
                className={`flex-1 py-2 text-sm font-medium rounded-lg transition-all ${
                  mode === m ? 'bg-white text-warm-800 shadow-sm' : 'text-warm-500 hover:text-warm-700'
                }`}
              >
                {m === 'login' ? t('auth_sign_in') : t('auth_sign_up')}
              </button>
            ))}
          </div>

          {/* Error message */}
          {error && (
            <div className="flex items-center gap-2 bg-rose-50 border border-rose-200 text-rose-600 text-sm px-4 py-3 rounded-lg mb-4">
              <AlertCircle size={15} className="shrink-0" />
              {error}
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            {mode === 'register' && (
              <div className="relative">
                <User size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-warm-400 pointer-events-none" />
                <input
                  type="text"
                  placeholder={t('auth_name')}
                  value={form.full_name}
                  onChange={set('full_name')}
                  className="input-field pl-10"
                />
              </div>
            )}

            <div className="relative">
              <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-warm-400 pointer-events-none" />
              <input
                type="email"
                placeholder={t('auth_email')}
                value={form.email}
                onChange={set('email')}
                required
                className="input-field pl-10"
              />
            </div>

            <div className="relative">
              <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-warm-400 pointer-events-none" />
              <input
                type="password"
                placeholder={t('auth_password')}
                value={form.password}
                onChange={set('password')}
                required
                minLength={6}
                className="input-field pl-10"
              />
            </div>

            <button type="submit" disabled={loading} className="btn-primary mt-1">
              {loading
                ? t('loading')
                : mode === 'login' ? t('auth_submit_login') : t('auth_submit_register')}
            </button>
          </form>

          {/* Switch */}
          <p className="text-center text-sm text-warm-400 mt-5">
            {mode === 'login' ? t('auth_no_account') : t('auth_have_account')}{' '}
            <button
              onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError('') }}
              className="text-health-600 font-medium hover:underline"
            >
              {mode === 'login' ? t('auth_sign_up') : t('auth_sign_in')}
            </button>
          </p>
        </div>
      </div>
    </div>
  )
}
