import { Check, Info, Minus, ShieldCheck, ShieldX, X } from 'lucide-react'

import { Badge } from '#/components/ui/badge'
import { scoreTone } from '#/components/score-gauge'
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
  if (eligibility.status === 'eligible') {
    return (
      <Badge variant="success" title={eligibility.summary}>
        <ShieldCheck aria-hidden />
        Eligible
      </Badge>
    )
  }
  if (eligibility.status === 'needs_verification') {
    return (
      <Badge variant="warning" title={eligibility.summary}>
        <Info aria-hidden />
        Requires verification
      </Badge>
    )
  }
  return (
    <Badge variant="danger" title={eligibility.summary}>
      <ShieldX aria-hidden />
      Eligibility concern
    </Badge>
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
    <div
      className="flex items-center gap-3"
      role="meter"
      aria-valuenow={pct}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={`${label}: ${score.toFixed(1)} of ${max}`}
    >
      <div className="text-2xl font-semibold tabular-nums tracking-tight text-[var(--ink)]">
        {score.toFixed(1)}
        <span className="ml-0.5 text-sm font-normal text-[var(--ink-tertiary)]">
          /{max}
        </span>
      </div>
      <div className="h-2 w-28 overflow-hidden rounded-full bg-[var(--panel)]">
        <div
          className="h-full rounded-full"
          style={{ width: `${pct}%`, background: scoreTone(pct) }}
        />
      </div>
    </div>
  )
}

export function DimensionBars({ breakdown }: { breakdown: DimensionScore[] }) {
  return (
    <div className="space-y-3">
      {breakdown.map((dimension) => {
        const pct = Math.round(dimension.percentage)
        return (
          <div key={dimension.key} className="text-xs">
            <div className="mb-1.5 flex items-baseline justify-between gap-2">
              <span className="text-sm font-medium text-[var(--ink)]">
                {dimension.label}
              </span>
              <span className="tabular-nums text-[var(--ink-secondary)]">
                {dimension.score.toFixed(1)} / {dimension.max_points}{' '}
                <span className="text-[var(--ink-tertiary)]">({pct}%)</span>
              </span>
            </div>
            <div className="h-1.5 w-full overflow-hidden rounded-full bg-[var(--panel)]">
              <div
                className="h-full rounded-full transition-[width] duration-500"
                style={{ width: `${pct}%`, background: scoreTone(pct) }}
              />
            </div>
            {((dimension.matched ?? []).length > 0 ||
              (dimension.missing ?? []).length > 0) && (
              <div className="mt-1.5 flex flex-wrap gap-1">
                {(dimension.matched ?? []).slice(0, 6).map((item) => (
                  <Badge
                    key={`m-${item}`}
                    variant="success"
                    className="px-2 py-0 text-[11px] font-normal"
                  >
                    <Check aria-hidden />
                    {item}
                  </Badge>
                ))}
                {(dimension.missing ?? []).slice(0, 4).map((item) => (
                  <Badge
                    key={`x-${item}`}
                    variant="danger"
                    className="px-2 py-0 text-[11px] font-normal"
                  >
                    <X aria-hidden />
                    {item}
                  </Badge>
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
          <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-[var(--ink-secondary)]">
            Why this matches
          </p>
          <ul className="m-0 list-none space-y-1.5 p-0 text-xs leading-relaxed text-[var(--ink-secondary)]">
            {strengths.map((strength) => (
              <li key={strength} className="flex gap-2">
                <Check
                  aria-hidden
                  className="mt-0.5 size-3.5 shrink-0 text-[var(--status-success)]"
                />
                {strength}
              </li>
            ))}
          </ul>
        </div>
      )}
      {gaps.length > 0 && (
        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-[var(--ink-secondary)]">
            Gaps &amp; concerns
          </p>
          <ul className="m-0 list-none space-y-1.5 p-0 text-xs leading-relaxed text-[var(--ink-secondary)]">
            {gaps.map((gap) => (
              <li key={gap} className="flex gap-2">
                <Minus
                  aria-hidden
                  className="mt-0.5 size-3.5 shrink-0 text-[var(--status-danger)]"
                />
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
    <ul className="m-0 list-none space-y-2 p-0 text-xs">
      {relevant.map((check) => (
        <li
          key={check.code + check.label}
          className="flex items-start gap-2 text-[var(--ink-secondary)]"
        >
          <Badge
            variant={
              check.status === 'pass'
                ? 'success-outline'
                : check.status === 'needs_verification'
                  ? 'warning-outline'
                  : 'danger-outline'
            }
            className="mt-0.5 shrink-0 px-1.5 py-0 font-semibold tracking-wide"
          >
            {check.status === 'pass'
              ? 'PASS'
              : check.status === 'needs_verification'
                ? 'VERIFY'
                : 'FAIL'}
          </Badge>
          <span className="leading-relaxed">
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
    <p className="m-0 flex gap-2.5 rounded-lg border border-dashed border-[var(--dashed-border)] bg-[var(--canvas-soft)] px-3.5 py-2.5 text-xs leading-relaxed text-[var(--ink-secondary)]">
      <Info
        aria-hidden
        className="mt-0.5 size-3.5 shrink-0 text-[var(--ink-tertiary)]"
      />
      {text}
    </p>
  )
}
