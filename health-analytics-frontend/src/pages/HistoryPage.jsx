import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Loader2, Trash2, TrendingUp, Plus, AlertCircle } from 'lucide-react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from 'recharts'
import api from '../api/api'
import { useLang } from '../context/LangContext'

const RISK_BADGE = {
  low:    'bg-health-100 text-health-700',
  medium: 'bg-amber-100  text-amber-700',
  high:   'bg-rose-100   text-rose-700',
}

export default function HistoryPage() {
  const { t } = useLang()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [deletingId, setDeletingId] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.get('/api/v1/health/history')
      .then((res) => setData(res.data))
      .catch(() => setError(t('error_generic')))
      .finally(() => setLoading(false))
  }, [])

  const handleDelete = async (id) => {
    if (!window.confirm('Удалить анализ?')) return
    setDeletingId(id)
    try {
      await api.delete(`/api/v1/health/analysis/${id}`)
      setData((prev) => ({
        ...prev,
        total: prev.total - 1,
        analyses: prev.analyses.filter((a) => a.id !== id),
      }))
    } catch {
      setError(t('error_generic'))
    } finally {
      setDeletingId(null)
    }
  }

  if (loading) return (
    <div className="min-h-screen pt-16 flex items-center justify-center">
      <Loader2 size={32} className="animate-spin text-health-500" />
    </div>
  )

  const analyses = data?.analyses || []
  const chartData = [...analyses].reverse().map((a) => ({
    date: new Date(a.created_at).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' }),
    score: a.health_score,
  }))

  return (
    <div className="min-h-screen pt-16 px-4 py-10 bg-warm-50">
      <div className="max-w-2xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-display text-2xl font-bold text-warm-900">{t('history_title')}</h1>
            <p className="text-sm text-warm-400 mt-1">{t('history_total')}: {data?.total || 0}</p>
          </div>
          <Link
            to="/analyze"
            className="flex items-center gap-1.5 px-4 py-2 bg-health-500 text-white text-sm font-medium rounded-xl hover:bg-health-600 transition-colors shadow-sm"
          >
            <Plus size={14} />{t('nav_analyze')}
          </Link>
        </div>

        {/* Error */}
        {error && (
          <div className="flex items-center gap-2 bg-rose-50 border border-rose-200 text-rose-600 text-sm px-4 py-3 rounded-xl">
            <AlertCircle size={15} />{error}
          </div>
        )}

        {/* Progress chart */}
        {chartData.length > 1 && (
          <div className="card">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp size={18} className="text-health-500" />
              <h2 className="font-semibold text-warm-800">{t('history_progress')}</h2>
            </div>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e7e5e4" />
                <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#a8a29e' }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: '#a8a29e' }} />
                <Tooltip
                  contentStyle={{
                    borderRadius: '10px',
                    border: '1px solid #e7e5e4',
                    boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)',
                  }}
                />
                <Line
                  type="monotone" dataKey="score"
                  stroke="#22c55e" strokeWidth={2.5}
                  dot={{ fill: '#22c55e', r: 4 }}
                  activeDot={{ r: 6 }}
                  name={t('history_score')}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Empty state */}
        {analyses.length === 0 && (
          <div className="card text-center py-16">
            <p className="text-warm-400 mb-4">{t('history_empty')}</p>
            <Link to="/analyze" className="btn-primary inline-flex items-center gap-2">
              <Plus size={16} />{t('history_go_analyze')}
            </Link>
          </div>
        )}

        {/* List */}
        <div className="space-y-3">
          {analyses.map((a) => (
            <div key={a.id} className="card hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 flex-wrap">
                    <span className="font-mono font-bold text-2xl text-warm-800">{a.health_score}</span>
                    <span className="text-sm text-warm-400">{t('history_score')}</span>
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${RISK_BADGE[a.risk_level]}`}>
                      {t(`risk_${a.risk_level}`)}
                    </span>
                  </div>
                  <div className="flex items-center gap-4 mt-1.5 text-sm text-warm-400 flex-wrap">
                    <span>BMI <span className="font-mono text-warm-600">{a.bmi.toFixed(1)}</span></span>
                    <span>{a.weight_kg} кг</span>
                    <span>{new Date(a.created_at).toLocaleDateString('ru-RU')}</span>
                  </div>
                </div>

                <div className="flex items-center gap-2 ml-4 shrink-0">
                  <Link
                    to={`/result/${a.id}`}
                    className="px-3 py-1.5 text-xs font-medium text-health-600 bg-health-50 rounded-lg hover:bg-health-100 transition-colors"
                  >
                    Открыть →
                  </Link>
                  <button
                    onClick={() => handleDelete(a.id)}
                    disabled={deletingId === a.id}
                    className="p-1.5 text-warm-300 hover:text-rose-400 hover:bg-rose-50 rounded-lg transition-colors"
                  >
                    {deletingId === a.id
                      ? <Loader2 size={14} className="animate-spin" />
                      : <Trash2 size={14} />}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
