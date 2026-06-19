import { Link } from 'react-router-dom'
import { Activity, Brain, Calendar, TrendingUp, ChevronRight, Shield } from 'lucide-react'
import { useLang } from '../context/LangContext'
import { useAuth } from '../context/AuthContext'

const FEATURES = [
  { icon: Activity, key: 'f1', color: 'text-health-500', bg: 'bg-health-50' },
  { icon: Brain,    key: 'f2', color: 'text-indigo-500', bg: 'bg-indigo-50' },
  { icon: Calendar, key: 'f3', color: 'text-teal-500',   bg: 'bg-teal-50'   },
  { icon: TrendingUp, key: 'f4', color: 'text-amber-500', bg: 'bg-amber-50' },
]

export default function LandingPage() {
  const { t } = useLang()
  const { token } = useAuth()

  return (
    <div className="min-h-screen pt-16">
      {/* Hero */}
      <section className="relative overflow-hidden bg-gradient-to-br from-warm-50 via-health-50/30 to-warm-50 py-24 px-4">
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-20 right-1/4 w-96 h-96 bg-health-100/40 rounded-full blur-3xl" />
          <div className="absolute bottom-0 left-1/4 w-64 h-64 bg-indigo-100/30 rounded-full blur-3xl" />
        </div>

        <div className="relative max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-health-100 text-health-700 text-sm font-medium px-4 py-2 rounded-full mb-8">
            <Shield size={14} />
            AI-Powered Health Analytics
          </div>

          <h1 className="font-display text-5xl sm:text-6xl font-bold text-warm-900 mb-6 leading-tight">
            {t('land_title')}
          </h1>

          <p className="text-xl text-warm-500 max-w-2xl mx-auto mb-10 leading-relaxed">
            {t('land_subtitle')}
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to={token ? '/analyze' : '/auth'}
              className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-health-500 text-white font-semibold rounded-xl hover:bg-health-600 active:bg-health-700 transition-all shadow-md hover:shadow-lg hover:-translate-y-0.5"
            >
              {t('land_cta')}
              <ChevronRight size={18} />
            </Link>
            {!token && (
              <Link
                to="/auth"
                className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-white text-warm-700 font-semibold rounded-xl border border-warm-200 hover:bg-warm-50 transition-all shadow-sm"
              >
                {t('land_login')}
              </Link>
            )}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="max-w-6xl mx-auto px-4 py-20">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {FEATURES.map(({ icon: Icon, key, color, bg }) => (
            <div
              key={key}
              className="bg-white rounded-2xl p-6 border border-warm-100 shadow-soft hover:shadow-md hover:-translate-y-1 transition-all duration-300"
            >
              <div className={`w-12 h-12 ${bg} rounded-xl flex items-center justify-center mb-4`}>
                <Icon size={22} className={color} />
              </div>
              <h3 className="font-semibold text-warm-800 mb-2">{t(`land_${key}_title`)}</h3>
              <p className="text-sm text-warm-500 leading-relaxed">{t(`land_${key}_desc`)}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Bottom CTA */}
      <section className="max-w-4xl mx-auto px-4 pb-20">
        <div className="bg-gradient-to-r from-health-500 to-health-600 rounded-3xl p-10 text-center text-white shadow-glow">
          <h2 className="font-display text-3xl font-semibold mb-4">{t('land_title')}</h2>
          <p className="text-health-100 mb-8 max-w-lg mx-auto">{t('land_subtitle')}</p>
          <Link
            to={token ? '/analyze' : '/auth'}
            className="inline-flex items-center gap-2 px-8 py-4 bg-white text-health-600 font-semibold rounded-xl hover:bg-health-50 transition-all shadow-md"
          >
            {t('land_cta')}
            <ChevronRight size={18} />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-warm-200 py-8 text-center text-sm text-warm-400">
        <div className="flex items-center justify-center gap-2">
          <Activity size={14} className="text-health-400" />
          <span>Health Analytics © 2024</span>
        </div>
        <p className="mt-2 text-xs max-w-md mx-auto">
          ⚠️ Система носит информационный характер и не является медицинским диагнозом.
        </p>
      </footer>
    </div>
  )
}
