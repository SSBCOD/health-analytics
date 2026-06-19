import { useEffect, useState } from 'react'
import { useParams, useLocation, useNavigate, Link } from 'react-router-dom'
import { Loader2, Plus, Clock, AlertCircle, CheckCircle, Stethoscope, HeartPulse } from 'lucide-react'
import api from '../api/api'
import { useLang } from '../context/LangContext'
import ScoreGauge from '../components/ScoreGauge'

const RISK_BADGE = {
  low:    'bg-health-100 text-health-700',
  medium: 'bg-amber-100  text-amber-700',
  high:   'bg-rose-100   text-rose-700',
}

function getBmiStyle(bmi) {
  if (bmi < 18.5) return { bg: 'bg-blue-50',   text: 'text-blue-600',   border: 'border-blue-200' }
  if (bmi < 25)   return { bg: 'bg-health-50',  text: 'text-health-600', border: 'border-health-200' }
  if (bmi < 30)   return { bg: 'bg-amber-50',   text: 'text-amber-600',  border: 'border-amber-200' }
  return             { bg: 'bg-rose-50',    text: 'text-rose-600',   border: 'border-rose-200' }
}

export default function ResultPage() {
  const { id } = useParams()
  const { state } = useLocation()
  const navigate = useNavigate()
  const { t } = useLang()

  const [result, setResult] = useState(state?.result || null)
  const [loading, setLoading] = useState(!result)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!result) {
      api.get(`/api/v1/health/analysis/${id}`)
        .then((res) => setResult(res.data))
        .catch(() => setError(t('error_generic')))
        .finally(() => setLoading(false))
    }
  }, [id])

  if (loading) return (
    <div className="min-h-screen pt-16 flex items-center justify-center">
      <Loader2 size={32} className="animate-spin text-health-500" />
    </div>
  )

  if (error) return (
    <div className="min-h-screen pt-16 flex items-center justify-center px-4">
      <div className="text-center">
        <AlertCircle size={40} className="text-rose-400 mx-auto mb-3" />
        <p className="text-warm-500 mb-4">{error}</p>
        <button onClick={() => navigate('/analyze')} className="btn-primary">{t('result_new')}</button>
      </div>
    </div>
  )

  const bmiStyle = getBmiStyle(result.bmi)

  return (
    <div className="min-h-screen pt-16 px-4 py-10 bg-warm-50">
      <div className="max-w-2xl mx-auto space-y-5">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h1 className="font-display text-2xl font-bold text-warm-900">{t('result_interpretation')}</h1>
          <span className="text-xs text-warm-400">
            {new Date(result.created_at).toLocaleDateString('ru-RU')}
          </span>
        </div>

        {/* Score + BMI */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="card flex flex-col items-center py-8">
            <p className="text-sm font-medium text-warm-500 mb-4">{t('result_score')}</p>
            <ScoreGauge score={result.health_score} />
            <div className={`mt-4 px-3 py-1 rounded-full text-xs font-medium ${RISK_BADGE[result.risk_level]}`}>
              {t(`risk_${result.risk_level}`)}
            </div>
          </div>

          <div className={`card border ${bmiStyle.border} ${bmiStyle.bg} flex flex-col`}>
            <p className="text-sm font-medium text-warm-500 mb-2">{t('result_bmi_full')}</p>
            <p className={`font-mono font-bold text-5xl ${bmiStyle.text} mb-1`}>
              {result.bmi.toFixed(1)}
            </p>
            <p className={`text-sm font-semibold ${bmiStyle.text} mb-4`}>{result.bmi_category}</p>

            <div className="border-t border-warm-200 pt-4 mt-auto">
              <p className="text-xs text-warm-500 font-medium mb-1">{t('result_ideal')}</p>
              <p className={`text-sm font-semibold ${bmiStyle.text}`}>
                {result.ideal_weight_min.toFixed(1)} – {result.ideal_weight_max.toFixed(1)} кг
              </p>
              {result.weight_difference !== 0 && (
                <p className="text-xs text-warm-400 mt-1">
                  {result.weight_difference > 0
                    ? `+${result.weight_difference.toFixed(1)} кг выше нормы`
                    : `${Math.abs(result.weight_difference).toFixed(1)} кг ниже нормы`}
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Interpretation */}
        <div className="card">
          <div className="flex items-center gap-2 mb-3">
            <HeartPulse size={18} className="text-health-500" />
            <h2 className="font-semibold text-warm-800">{t('result_interpretation')}</h2>
          </div>
          <p className="text-warm-600 text-sm leading-relaxed whitespace-pre-line">{result.interpretation}</p>
        </div>

        {/* Positive feedback */}
        {result.positive_feedback && (
          <div className="card border-health-200 bg-health-50">
            <div className="flex items-start gap-3">
              <CheckCircle size={18} className="text-health-500 mt-0.5 shrink-0" />
              <div>
                <h3 className="font-semibold text-health-800 mb-1">{t('result_positive')}</h3>
                <p className="text-health-700 text-sm leading-relaxed">{result.positive_feedback}</p>
              </div>
            </div>
          </div>
        )}

        {/* Doctor recommendation */}
        {result.doctor_recommendation && (
          <div className="card border-amber-200 bg-amber-50">
            <div className="flex items-start gap-3">
              <Stethoscope size={18} className="text-amber-600 mt-0.5 shrink-0" />
              <div>
                <h3 className="font-semibold text-amber-800 mb-1">{t('result_doctor')}</h3>
                <p className="text-amber-700 text-sm leading-relaxed">{result.doctor_recommendation}</p>
              </div>
            </div>
          </div>
        )}

        {/* Weekly plan */}
        {result.weekly_plan && result.weekly_plan.length > 0 && (
          <div className="card">
            <h2 className="font-semibold text-warm-800 mb-4">{t('result_weekly')}</h2>
            <div className="space-y-3">
              {result.weekly_plan.map((day, i) => (
                <div key={i} className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-health-100 rounded-full flex items-center justify-center shrink-0 mt-0.5">
                    <span className="text-xs font-bold text-health-600">{i + 1}</span>
                  </div>
                  <p className="text-sm text-warm-600 leading-relaxed">{day}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Disclaimer */}
        {result.disclaimer && (
          <div className="bg-warm-100 rounded-xl px-4 py-3">
            <p className="text-xs text-warm-400 leading-relaxed">
              <span className="font-medium text-warm-500">{t('result_disclaimer')}: </span>
              {result.disclaimer}
            </p>
          </div>
        )}

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-3 pt-1">
          <Link to="/analyze" className="btn-primary flex-1 flex items-center justify-center gap-2">
            <Plus size={16} />{t('result_new')}
          </Link>
          <Link to="/history" className="btn-secondary flex-1 flex items-center justify-center gap-2">
            <Clock size={16} />{t('result_history')}
          </Link>
        </div>
      </div>
    </div>
  )
}
