import { Link, useNavigate, useLocation } from 'react-router-dom'
import { Activity, Clock, BarChart3, LogOut, Menu, X } from 'lucide-react'
import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { useLang } from '../context/LangContext'

export default function Navbar() {
  const { token, logout, user } = useAuth()
  const { lang, setLang, t } = useLang()
  const navigate = useNavigate()
  const location = useLocation()
  const [open, setOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/')
    setOpen(false)
  }

  const isActive = (path) => location.pathname === path

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-warm-100">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2.5">
          <div className="w-8 h-8 bg-gradient-to-br from-health-500 to-health-600 rounded-lg flex items-center justify-center shadow-sm">
            <Activity size={16} className="text-white" strokeWidth={2.5} />
          </div>
          <span className="font-display font-semibold text-warm-800 text-lg">Health</span>
        </Link>

        {/* Desktop links */}
        <div className="hidden md:flex items-center gap-1">
          {token && (
            <>
              <Link
                to="/analyze"
                className={`flex items-center gap-1.5 px-3 py-2 text-sm rounded-lg transition-colors ${
                  isActive('/analyze')
                    ? 'bg-health-50 text-health-700 font-medium'
                    : 'text-warm-600 hover:text-warm-900 hover:bg-warm-100'
                }`}
              >
                <BarChart3 size={15} />
                {t('nav_analyze')}
              </Link>
              <Link
                to="/history"
                className={`flex items-center gap-1.5 px-3 py-2 text-sm rounded-lg transition-colors ${
                  isActive('/history')
                    ? 'bg-health-50 text-health-700 font-medium'
                    : 'text-warm-600 hover:text-warm-900 hover:bg-warm-100'
                }`}
              >
                <Clock size={15} />
                {t('nav_history')}
              </Link>
            </>
          )}
        </div>

        <div className="hidden md:flex items-center gap-3">
          {/* Language switcher */}
          <div className="flex items-center bg-warm-100 rounded-lg p-0.5">
            {['kk', 'ru'].map((l) => (
              <button
                key={l}
                onClick={() => setLang(l)}
                className={`px-2.5 py-1 text-xs font-medium rounded-md transition-all ${
                  lang === l ? 'bg-white shadow-sm text-warm-800' : 'text-warm-500 hover:text-warm-700'
                }`}
              >
                {l.toUpperCase()}
              </button>
            ))}
          </div>

          {token ? (
            <div className="flex items-center gap-3">
              {user?.full_name && (
                <span className="text-sm text-warm-500">{user.full_name.split(' ')[0]}</span>
              )}
              <button
                onClick={handleLogout}
                className="flex items-center gap-1.5 text-sm text-warm-400 hover:text-rose-500 transition-colors"
              >
                <LogOut size={14} />
                {t('nav_logout')}
              </button>
            </div>
          ) : (
            <Link
              to="/auth"
              className="px-4 py-2 bg-health-500 text-white text-sm font-medium rounded-lg hover:bg-health-600 transition-colors shadow-sm"
            >
              {t('auth_login')}
            </Link>
          )}
        </div>

        {/* Mobile toggle */}
        <button className="md:hidden p-2 text-warm-600" onClick={() => setOpen(!open)}>
          {open ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Mobile menu */}
      {open && (
        <div className="md:hidden bg-white border-t border-warm-100 px-4 py-3 flex flex-col gap-1 shadow-lg">
          {token && (
            <>
              <Link to="/analyze" onClick={() => setOpen(false)}
                className="flex items-center gap-2 px-3 py-2.5 text-sm text-warm-700 rounded-lg hover:bg-warm-50">
                <BarChart3 size={16} className="text-health-500" />{t('nav_analyze')}
              </Link>
              <Link to="/history" onClick={() => setOpen(false)}
                className="flex items-center gap-2 px-3 py-2.5 text-sm text-warm-700 rounded-lg hover:bg-warm-50">
                <Clock size={16} className="text-health-500" />{t('nav_history')}
              </Link>
            </>
          )}
          <div className="flex gap-2 px-3 py-2">
            {['kk', 'ru'].map((l) => (
              <button key={l} onClick={() => setLang(l)}
                className={`px-3 py-1.5 text-sm rounded-lg transition-all ${
                  lang === l ? 'bg-health-100 text-health-700 font-medium' : 'text-warm-500 bg-warm-100'
                }`}>
                {l === 'kk' ? 'Қазақша' : 'Русский'}
              </button>
            ))}
          </div>
          {token ? (
            <button onClick={handleLogout}
              className="flex items-center gap-2 px-3 py-2.5 text-sm text-rose-500 rounded-lg hover:bg-rose-50">
              <LogOut size={16} />{t('nav_logout')}
            </button>
          ) : (
            <Link to="/auth" onClick={() => setOpen(false)}
              className="px-3 py-2.5 text-sm text-health-600 font-medium rounded-lg hover:bg-health-50">
              {t('auth_login')}
            </Link>
          )}
        </div>
      )}
    </nav>
  )
}
