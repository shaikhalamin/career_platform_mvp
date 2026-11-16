import { cn } from 'cn'

/**
 * The hero match-score display: animated circular gauge with the score in
 * tabular numerals at its centre. Ring colour follows the score band —
 * brand blue (strong), amber (partial), red (weak) — mirroring the
 * dimension-bar semantics used across the app.
 *
 * The fill animates from empty via CSS (`gauge-fill` keyframes in
 * styles.css); `prefers-reduced-motion` disables it globally.
 */
export function scoreTone(percent: number): string {
  if (percent >= 80) return 'var(--primary)'
  if (percent >= 50) return 'var(--status-warning)'
  return 'var(--status-danger)'
}

export function ScoreGauge({
  score,
  max,
  size = 'lg',
  label = 'Match score',
  className,
}: {
  score: number
  max: number
  size?: 'sm' | 'lg'
  label?: string
  className?: string
}) {
  const pct = max > 0 ? Math.max(0, Math.min(100, (score / max) * 100)) : 0
  const tone = scoreTone(pct)

  const geometry = size === 'lg' ? { r: 52, stroke: 10 } : { r: 26, stroke: 5 }
  const circumference = 2 * Math.PI * geometry.r
  const offset = circumference * (1 - pct / 100)

  return (
    <div
      className={cn('relative inline-flex shrink-0', className)}
      role="meter"
      aria-valuenow={Math.round(pct)}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={`${label}: ${score.toFixed(1)} of ${max}`}
    >
      <svg
        width={size === 'lg' ? 128 : 64}
        height={size === 'lg' ? 128 : 64}
        viewBox="0 0 128 128"
        aria-hidden
        className="-rotate-90"
      >
        <circle
          cx="64"
          cy="64"
          r={geometry.r}
          fill="none"
          stroke="var(--panel)"
          strokeWidth={geometry.stroke}
        />
        <circle
          cx="64"
          cy="64"
          r={geometry.r}
          fill="none"
          stroke={tone}
          strokeWidth={geometry.stroke}
          strokeLinecap="round"
          strokeDasharray={circumference}
          className="gauge-arc"
          style={
            {
              '--gauge-circ': circumference,
              '--gauge-offset': offset,
            } as React.CSSProperties
          }
        />
      </svg>
      <span
        className={
          size === 'lg'
            ? 'absolute inset-0 flex flex-col items-center justify-center'
            : 'absolute inset-0 flex items-center justify-center'
        }
      >
        <span
          className={cn(
            'font-semibold tabular-nums text-[var(--ink)]',
            size === 'lg' ? 'text-3xl tracking-tight' : 'text-base',
          )}
        >
          {Math.round(score)}
        </span>
        {size === 'lg' && (
          <span className="mt-0.5 text-xs tabular-nums text-[var(--ink-tertiary)]">
            / {max} pts
          </span>
        )}
      </span>
    </div>
  )
}
