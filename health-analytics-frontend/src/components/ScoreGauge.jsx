export default function ScoreGauge({ score }) {
  const radius = 70
  const circumference = 2 * Math.PI * radius
  const safeScore = Math.max(0, Math.min(100, score ?? 0))
  const offset = circumference * (1 - safeScore / 100)
  const color = safeScore >= 70 ? '#22c55e' : safeScore >= 40 ? '#f59e0b' : '#f43f5e'

  const label =
    safeScore >= 80 ? 'Отлично' :
    safeScore >= 70 ? 'Хорошо' :
    safeScore >= 50 ? 'Средне' :
    safeScore >= 30 ? 'Плохо' : 'Критично'

  return (
    <div className="flex flex-col items-center gap-1">
      <div className="relative" style={{ width: 180, height: 180 }}>
        <svg width="180" height="180" style={{ transform: 'rotate(-90deg)' }}>
          <circle
            cx="90" cy="90" r={radius}
            fill="none" stroke="#e7e5e4" strokeWidth="12"
          />
          <circle
            cx="90" cy="90" r={radius}
            fill="none" stroke={color} strokeWidth="12"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="font-mono font-bold text-4xl" style={{ color }}>
            {safeScore}
          </span>
          <span className="text-xs text-warm-400">/100</span>
        </div>
      </div>
      <span className="text-sm font-semibold" style={{ color }}>{label}</span>
    </div>
  )
}
