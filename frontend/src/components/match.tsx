import type { DimensionScoreRead } from '#/gen/types/DimensionScoreRead'
import type { EligibilityRead } from '#/gen/types/EligibilityRead'

/**
 * Shared match-visualisation pieces: eligibility badges, score meters,
 * per-dimension breakdown bars and the strengths/gaps explanation lists.
 */

export type DimensionScore = DimensionScoreRead
export type Eligibility = EligibilityRead

export function EligibilityBadge({
  eligibility,
}: {
  eligibility: Eligibility
}) {
  const tone =
    eligibility.status === 'eligible'
      ? 'bg-[color-mix(in_oklab,var(--primary)_12%,transparent)] text-[var(--primary)] border-[color-mix(in_oklab,var(--primary)_35%,transparent)]'
      : eligibility.status === 'needs_verification'
        ? 'bg-[color-mix(in_oklab,var(--tier-orange)_12%,transparent)] text-[var(--tier-orange)] border-[color-mix(in_oklab,var(--tier-orange)_40%,transparent)]'
        : 'bg-[color-mix(in_oklab,var(--error)_10%,transparent)] text-[var(--error)] border-[color-mix(in_oklab,var(--error)_35%,transparent)]'

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-semibold ${tone}`}
      title={eligibility.summary}
    >
      {eligibility.status === 'eligible'
        ? 'Eligible (automated check)'
        : eligibility.status === 'needs_verification'
          ? '⚠ Requires verification'
          : '✕ Eligibility concern'}
    </span>
  )
}

export function ScoreMeter({
  score,
  max,
  label = 'Match score',
}: {
  score: number
  max: number
  label?: string
}) {
  const pct = max > 0 ? Math.round((score / max) * 100) : 0
  return (
    <div className="flex items-center gap-3">
      <div className="text-2xl font-semibold tabular-nums text-[var(--ink)]">
        {score.toFixed(1)}
        <span className="ml-0.5 text-sm font-normal text-[var(--ink-tertiary)]">
          /{max}
        </span>
      </div>
      <div
        className="h-2 w-28 overflow-hidden rounded-full bg-[var(--fog)]"
        role="meter"
        aria-valuenow={pct}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={label}
      >
        <div
          className="h-full rounded-full bg-[var(--primary)]"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}

export function DimensionBars({ breakdown }: { breakdown: DimensionScore[] }) {
  return (
    <div className="space-y-2.5">
      {breakdown.map((dimension) => {
        const pct = Math.round(dimension.percentage)
        return (
          <div key={dimension.key} className="text-xs">
            <div className="mb-1 flex items-baseline justify-between gap-2">
              <span className="font-semibold text-[var(--ink)]">
                {dimension.label}
              </span>
              <span className="tabular-nums text-[var(--ink-secondary)]">
                {dimension.score.toFixed(1)} / {dimension.max_points}{' '}
                <span className="text-[var(--ink-tertiary)]">({pct}%)</span>
              </span>
            </div>
            <div className="h-1.5 w-full overflow-hidden rounded-full bg-[var(--fog)]">
              <div
                className={`h-full rounded-full ${
                  pct >= 80
                    ? 'bg-[var(--primary)]'
                    : pct >= 50
                      ? 'bg-[var(--badge-orange)]'
                      : 'bg-[var(--error)]'
                }`}
                style={{ width: `${pct}%` }}
              />
            </div>
            {((dimension.matched ?? []).length > 0 ||
              (dimension.missing ?? []).length > 0) && (
              <div className="mt-1 flex flex-wrap gap-1">
                {(dimension.matched ?? []).slice(0, 6).map((item) => (
                  <span
                    key={`m-${item}`}
                    className="rounded-sm bg-[color-mix(in_oklab,var(--primary)_10%,transparent)] px-1.5 py-0.5 text-[10px] text-[var(--primary)]"
                  >
                    ✓ {item}
                  </span>
                ))}
                {(dimension.missing ?? []).slice(0, 4).map((item) => (
                  <span
                    key={`x-${item}`}
                    className="rounded-sm bg-[color-mix(in_oklab,var(--error)_8%,transparent)] px-1.5 py-0.5 text-[10px] text-[var(--error)]"
                  >
                    ✕ {item}
                  </span>
                ))}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

export function ExplanationLists({
  strengths,
  gaps,
}: {
  strengths: string[]
  gaps: string[]
}) {
  if (strengths.length === 0 && gaps.length === 0) return null
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {strengths.length > 0 && (
        <div>
          <p className="mb-1.5 text-xs font-bold uppercase tracking-wider text-[var(--ink-secondary)]">
            Why this matches
          </p>
          <ul className="m-0 list-none space-y-1 p-0 text-xs text-[var(--ink-secondary)]">
            {strengths.map((strength) => (
              <li key={strength} className="flex gap-1.5">
                <span className="text-[var(--primary)]">+</span>
                {strength}
              </li>
            ))}
          </ul>
        </div>
      )}
      {gaps.length > 0 && (
        <div>
          <p className="mb-1.5 text-xs font-bold uppercase tracking-wider text-[var(--ink-secondary)]">
            Gaps &amp; concerns
          </p>
          <ul className="m-0 list-none space-y-1 p-0 text-xs text-[var(--ink-secondary)]">
            {gaps.map((gap) => (
              <li key={gap} className="flex gap-1.5">
                <span className="text-[var(--error)]">−</span>
                {gap}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export function EligibilityChecks({
  eligibility,
}: {
  eligibility: Eligibility
}) {
  const relevant = eligibility.checks.filter(
    (check) => check.status !== 'not_applicable',
  )
  if (relevant.length === 0) {
    return (
      <p className="m-0 text-xs text-[var(--ink-secondary)]">
        No hard constraints declared for this role.
      </p>
    )
  }
  return (
    <ul className="m-0 list-none space-y-1.5 p-0 text-xs">
      {relevant.map((check) => (
        <li
          key={check.code + check.label}
          className="flex items-start gap-2 text-[var(--ink-secondary)]"
        >
          <span
            className={`mt-0.5 inline-block shrink-0 rounded-sm px-1.5 py-0.5 text-[10px] font-bold ${
              check.status === 'pass'
                ? 'bg-[color-mix(in_oklab,var(--primary)_12%,transparent)] text-[var(--primary)]'
                : check.status === 'needs_verification'
                  ? 'bg-[color-mix(in_oklab,var(--tier-orange)_12%,transparent)] text-[var(--tier-orange)]'
                  : 'bg-[color-mix(in_oklab,var(--error)_10%,transparent)] text-[var(--error)]'
            }`}
          >
            {check.status === 'pass'
              ? 'PASS'
              : check.status === 'needs_verification'
                ? 'VERIFY'
                : 'FAIL'}
          </span>
          <span>
            <span className="font-semibold text-[var(--ink)]">
              {check.label}:
            </span>{' '}
            {check.evidence}
          </span>
        </li>
      ))}
    </ul>
  )
}

export function DisclaimerNote({ text }: { text: string }) {
  return (
    <p className="m-0 rounded-md border border-dashed border-[var(--dashed-border)] bg-[var(--canvas-soft)] px-3 py-2 text-[11px] leading-relaxed text-[var(--ink-secondary)]">
      ℹ {text}
    </p>
  )
}
