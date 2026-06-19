import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Loader2, AlertCircle, Sparkles } from 'lucide-react'
import api from '../api/api'
import { useLang } from '../context/LangContext'

export default function AnalyzePage() {
  const { t, apiLang } = useLang()
  const navigate = useNavigate()

  const [form, setForm] = useState({
    age: '',
    gender: '',
    height_cm: '',
    weight_kg: '',
    symptoms_text: '',
    language: apiLang,
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const set = (field) => (e) => setForm((prev) => ({ ...prev, [field]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (form.symptoms_text.trim().length < 10) {
      setError('Минимум 10 символов в описании симптомов')
      return
    }
    setLoading(true)
    setError('')
    try {
      const res = await api.post('/api/v1/health/analyze', {
        age: parseInt(form.age),
        gender: form.gender,
        height_cm: parseFloat(form.height_cm),
        weight_kg: parseFloat(form.weight_kg),
        symptoms_text: form.symptoms_text.trim(),
        language: form.language,
      })
      navigate(`/result/${res.data.id}`, { state: { result: res.data } })
    } catch (err) {
      setError(err.response?.data?.detail || t('error_generic'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen pt-16 px-4 py-10 bg-warm-50">
      <div className="max-w-xl mx-auto">
        <div className="mb-8">
          <h1 className="font-display text-3xl font-bold text-warm-900">{t('analyze_title')}</h1>
          <p className="text-warm-500 mt-2">{t('analyze_subtitle')}</p>
        </div>

        {error && (
          <div className="flex items-start gap-2 bg-rose-50 border border-rose-200 text-rose-600 text-sm px-4 py-3 rounded-xl mb-6">
            <AlertCircle size={15} className="mt-0.5 shrink-0" />
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="card flex flex-col gap-5">
          {/* Age & Gender */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-warm-700 mb-1.5">{t('analyze_age')}</label>
              <input
                type="number" placeholder="25"
                value={form.age} onChange={set('age')}
                min="1" max="120" required
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-warm-700 mb-1.5">{t('analyze_gender')}</label>
              <select value={form.gender} onChange={set('gender')} required className="input-field">
                <option value="">{t('select_gender')}</option>
                <option value="male">{t('analyze_male')}</option>
                <option value="female">{t('analyze_female')}</option>
              </select>
            </div>
          </div>

          {/* Height & Weight */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-warm-700 mb-1.5">{t('analyze_height')}</label>
              <input
                type="number" placeholder="175"
                value={form.height_cm} onChange={set('height_cm')}
                min="50" max="300" required
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-warm-700 mb-1.5">{t('analyze_weight')}</label>
              <input
                type="number" placeholder="70"
                value={form.weight_kg} onChange={set('weight_kg')}
                min="10" max="500" required
                className="input-field"
              />
            </div>
          </div>

          {/* Symptoms */}
          <div>
            <label className="block text-sm font-medium text-warm-700 mb-1.5">{t('analyze_symptoms')}</label>
            <textarea
              placeholder={t('analyze_symptoms_placeholder')}
              value={form.symptoms_text}
              onChange={set('symptoms_text')}
              required rows={5}
              className="input-field resize-none"
            />
            <p className="text-xs text-warm-400 mt-1 text-right">
              {form.symptoms_text.length} / 5000
            </p>
          </div>

          {/* Language */}
          <div>
            <label className="block text-sm font-medium text-warm-700 mb-1.5">{t('analyze_lang')}</label>
            <select value={form.language} onChange={set('language')} className="input-field">
              <option value="kz">{t('analyze_lang_kz')}</option>
              <option value="ru">{t('analyze_lang_ru')}</option>
            </select>
          </div>

          {/* Submit */}
          <button type="submit" disabled={loading} className="btn-primary flex items-center justify-center gap-2 mt-1">
            {loading ? (
              <><Loader2 size={18} className="animate-spin" />{t('analyze_loading')}</>
            ) : (
              <><Sparkles size={18} />{t('analyze_submit')}</>
            )}
          </button>
        </form>
      </div>
    </div>
  )
}
