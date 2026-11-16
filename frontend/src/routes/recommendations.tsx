import { useState } from 'react'
import { createFileRoute, Link } from '@tanstack/react-router'
import { ChevronDown } from 'lucide-react'

import {
  DisclaimerNote,
  DimensionBars,
  EligibilityBadge,
  EligibilityChecks,
  ExplanationLists,
  ScoreMeter,
} from '#/components/match'
import { ShortlistButton } from '#/components/shortlist-button'
import { useActiveProfile } from '#/lib/active-profile'
import { useGetRecommendationsApiV1RecommendationsGet } from '#/gen/queries/recommendations/useGetRecommendationsApiV1RecommendationsGet'
import type { RecommendationItem } from '#/gen/types/RecommendationItem'

export const Route = createFileRoute('/recommendations')({
  component: RecommendationsPage,
})

const EMPLOYMENT_LABELS: Record<string, string> = {
  full_time: 'Full-time',
  internship: 'Internship',
  contract: 'Contract',
  part_time: 'Part-time',
}

function RecommendationsPage() {
  const { activeProfileId } = useActiveProfile()
  const [topK, setTopK] = useState(20)
  const [expanded, setExpanded] = useState<string | null>(null)

  if (activeProfileId === null) {
    return (
      <main className="page-wrap py-16">
        <div className="panel-card mx-auto max-w-lg p-8 text-center">
          <h1 className="display-title m-0 text-2xl">Who are we matching?</h1>
          <p className="mt-3 text-sm text-[var(--ink-secondary)]">
            Pick an existing profile or create one — recommendations are
            computed live from it.
          </p>
          <div className="mt-6 flex justify-center gap-3">
            <Link to="/profiles" className="pill-outline">
              Choose a profile
            </Link>
            <Link to="/profiles/new" className="pill-primary">
              Create a profile
            </Link>
          </div>
        </div>
      </main>
    )
  }

  return (
    <RecommendationsList
      profileId={activeProfileId}
      topK={topK}
      onTopKChange={setTopK}
      expanded={expanded}
      onExpand={setExpanded}
    />
  )
}

function RecommendationsList({
  profileId,
  topK,
  onTopKChange,
  expanded,
  onExpand,
}: {
  profileId: number
  topK: number
  onTopKChange: (value: number) => void
  expanded: string | null
  onExpand: (id: string | null) => void
}) {
  const query = useGetRecommendationsApiV1RecommendationsGet({
    query: { profile_id: profileId, top_k: topK },
  })

  if (query.isPending) {
    return (
      <main className="page-wrap py-10">
        <p className="text-sm text-[var(--ink-secondary)]">
          Ranking opportunities…
        </p>
      </main>
    )
  }

  if (query.isError || !query.data.data) {
    return (
      <main className="page-wrap py-10">
        <p className="text-sm font-semibold text-red-600">
          Failed to load recommendations — is the backend running on port 8000?
        </p>
      </main>
    )
  }

  const data = query.data.data
  const items = data.items

  return (
    <main className="page-wrap py-10">
      <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="tier-eyebrow mb-2">
            Recommendations · recalculated live
          </p>
          <h1 className="display-title m-0 text-3xl font-semibold tracking-tight text-[var(--ink)]">
            Top matches for {data.profile_name}
          </h1>
          <p className="mt-2 text-sm text-[var(--ink-secondary)]">
            {data.retrieved_count} of {data.total_opportunities} opportunities ·
            ranked by eligibility first, then six-part match score
          </p>
        </div>
        <label className="flex items-center gap-2 text-xs text-[var(--ink-secondary)]">
          Show top
          <select
            value={topK}
            onChange={(e) => onTopKChange(Number(e.target.value))}
            className="rounded-md border border-[var(--input-border)] bg-transparent px-2 py-1.5 text-sm"
          >
            {[10, 20, 30, 50].map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="mb-6">
        <DisclaimerNote text={data.disclaimer} />
      </div>

      <div className="space-y-4">
        {items.map((item) => (
          <RecommendationCard
            key={item.opportunity.id}
            item={item}
            profileId={profileId}
            expanded={expanded === item.opportunity.id}
            onToggle={() =>
              onExpand(
                expanded === item.opportunity.id ? null : item.opportunity.id,
              )
            }
          />
        ))}
      </div>

      <p className="mt-6 text-center text-xs text-[var(--ink-tertiary)]">
        Weights: Skills 35 · Experience 20 · Education 15 · Location 15 ·
        Language 10 · Interests 5 — see{' '}
        <Link to="/about" className="underline">
          how matching works
        </Link>
        .
      </p>
    </main>
  )
}

function RecommendationCard({
  item,
  profileId,
  expanded,
  onToggle,
}: {
  item: RecommendationItem
  profileId: number | null
  expanded: boolean
  onToggle: () => void
}) {
  const opportunity = item.opportunity
  return (
    <article className="panel-card p-5">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <div className="mb-1 flex items-center gap-2">
            <span className="inline-flex size-7 items-center justify-center rounded-full bg-[var(--fog)] text-xs font-bold text-[var(--ink-secondary)]">
              {item.rank}
            </span>
            <Link
              to="/opportunities/$opportunityId"
              params={{ opportunityId: opportunity.id }}
              className="text-base font-semibold text-[var(--ink)] no-underline hover:underline"
            >
              {opportunity.title}
            </Link>
          </div>
          <p className="m-0 text-xs text-[var(--ink-secondary)]">
            {opportunity.organisation} ·{' '}
            {opportunity.city ? `${opportunity.city}, ` : ''}
            {opportunity.country} ·{' '}
            {EMPLOYMENT_LABELS[opportunity.employment_type] ??
              opportunity.employment_type}{' '}
            · {opportunity.min_years}–{opportunity.max_years} yrs
          </p>
          <div className="mt-2 flex flex-wrap gap-1">
            {opportunity.required_skills.slice(0, 4).map((skill) => (
              <span
                key={skill}
                className="rounded-sm bg-[var(--fog)] px-1.5 py-0.5 text-[10px] text-[var(--ink-secondary)]"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
        <div className="flex flex-col items-end gap-2">
          <ScoreMeter score={item.total_score} max={item.max_score} />
          <EligibilityBadge eligibility={item.eligibility} />
        </div>
      </div>

      <div className="mt-4 border-t border-[var(--divider)] pt-3">
        <ExplanationLists strengths={item.strengths} gaps={item.gaps} />
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-2">
        <ShortlistButton
          profileId={profileId}
          opportunityId={opportunity.id}
          shortlisted={item.shortlisted ?? false}
        />
        <Link
          to="/opportunities/$opportunityId"
          params={{ opportunityId: opportunity.id }}
          className="text-xs font-semibold text-[var(--link-blue)] underline-offset-2 hover:underline"
        >
          View details →
        </Link>
        <button
          type="button"
          onClick={onToggle}
          aria-expanded={expanded}
          className="ml-auto inline-flex items-center gap-1 text-xs font-semibold text-[var(--ink-secondary)] hover:text-[var(--ink)]"
        >
          {expanded ? 'Hide score breakdown' : 'Why this score?'}
          <ChevronDown
            className={`size-3.5 transition-transform ${expanded ? 'rotate-180' : ''}`}
          />
        </button>
      </div>

      {expanded && (
        <div className="mt-4 grid gap-5 border-t border-[var(--divider)] pt-4 sm:grid-cols-2">
          <div>
            <p className="mb-2 text-xs font-bold uppercase tracking-wider text-[var(--ink-secondary)]">
              Six-part score · cosine {item.cosine_similarity.toFixed(3)}
            </p>
            <DimensionBars breakdown={item.score_breakdown} />
          </div>
          <div>
            <p className="mb-2 text-xs font-bold uppercase tracking-wider text-[var(--ink-secondary)]">
              Eligibility evidence
            </p>
            <EligibilityChecks eligibility={item.eligibility} />
          </div>
        </div>
      )}
    </article>
  )
}
