import { useState } from 'react'
import { createFileRoute, Link } from '@tanstack/react-router'
import { ChevronDown, CircleAlert, Compass, Trophy } from 'lucide-react'

import { Badge } from '#/components/ui/badge'
import { Button } from '#/components/ui/button'
import { PageHeader } from '#/components/page-header'
import { EmptyState } from '#/components/empty-state'
import { ListRowsSkeleton } from '#/components/skeletons'
import { ScoreGauge } from '#/components/score-gauge'
import {
  DisclaimerNote,
  DimensionBars,
  EligibilityBadge,
  EligibilityChecks,
  ExplanationLists,
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
        <EmptyState
          icon={Compass}
          title="Who are we matching?"
          description="Pick an existing profile or create one — recommendations are computed live from it."
          actions={
            <>
              <Button asChild variant="outline">
                <Link to="/profiles">Choose a profile</Link>
              </Button>
              <Button asChild>
                <Link to="/profiles/new">Create a profile</Link>
              </Button>
            </>
          }
        />
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
        <PageHeader
          eyebrow="Recommendations · recalculated live"
          title="Top matches"
        />
        <ListRowsSkeleton count={4} />
      </main>
    )
  }

  if (query.isError || !query.data.data) {
    return (
      <main className="page-wrap py-10">
        <PageHeader
          eyebrow="Recommendations · recalculated live"
          title="Top matches"
        />
        <div
          role="alert"
          className="flex items-center gap-3 rounded-xl border border-[color-mix(in_oklab,var(--error)_30%,transparent)] bg-[color-mix(in_oklab,var(--error)_6%,transparent)] px-5 py-4 text-sm font-medium text-[var(--error)]"
        >
          <CircleAlert aria-hidden className="size-5 shrink-0" />
          Failed to load recommendations — is the backend running on port 8000?
        </div>
      </main>
    )
  }

  const data = query.data.data
  const items = data.items

  return (
    <main className="page-wrap py-10">
      <PageHeader
        eyebrow="Recommendations · recalculated live"
        title={`Top matches for ${data.profile_name}`}
        description={`${data.retrieved_count} of ${data.total_opportunities} opportunities · ranked by eligibility first, then six-part match score`}
        actions={
          <label className="flex items-center gap-2 text-sm text-[var(--ink-secondary)]">
            Show top
            <select
              value={topK}
              onChange={(e) => onTopKChange(Number(e.target.value))}
              className="rounded-lg border border-[var(--input-border)] bg-[var(--canvas)] px-2.5 py-1.5 text-sm font-medium text-[var(--ink)]"
            >
              {[10, 20, 30, 50].map((value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              ))}
            </select>
          </label>
        }
      />

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

      <p className="mt-8 text-center text-xs text-[var(--ink-tertiary)]">
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
  const topRank = item.rank === 1

  return (
    <article className="panel-card is-interactive p-5 sm:p-6">
      <div className="flex flex-wrap items-start gap-x-5 gap-y-4">
        {/* Rank tile */}
        <span
          aria-hidden
          className={`inline-flex size-10 shrink-0 items-center justify-center rounded-xl text-sm font-bold tabular-nums ${
            topRank
              ? 'bg-[color-mix(in_oklab,var(--tier-orange)_15%,transparent)] text-[var(--tier-orange)]'
              : 'bg-[var(--panel)] text-[var(--ink-secondary)]'
          }`}
        >
          {topRank ? <Trophy className="size-4.5" /> : item.rank}
        </span>

        <div className="min-w-0 flex-1">
          <div className="mb-1 flex flex-wrap items-center gap-2">
            <Link
              to="/opportunities/$opportunityId"
              params={{ opportunityId: opportunity.id }}
              className="text-base font-semibold text-[var(--ink)] no-underline hover:underline"
            >
              {opportunity.title}
            </Link>
            {topRank && <Badge variant="warning">Best match</Badge>}
          </div>
          <p className="m-0 text-xs text-[var(--ink-secondary)]">
            {opportunity.organisation} ·{' '}
            {opportunity.city ? `${opportunity.city}, ` : ''}
            {opportunity.country} ·{' '}
            {EMPLOYMENT_LABELS[opportunity.employment_type] ??
              opportunity.employment_type}{' '}
            · {opportunity.min_years}–{opportunity.max_years} yrs
          </p>
          <div className="mt-2.5 flex flex-wrap gap-1.5">
            {opportunity.required_skills.slice(0, 4).map((skill) => (
              <Badge
                key={skill}
                variant="secondary"
                className="px-2 py-0 font-normal"
              >
                {skill}
              </Badge>
            ))}
          </div>
        </div>

        <div className="flex shrink-0 items-center gap-4">
          <ScoreGauge score={item.total_score} max={item.max_score} size="sm" />
          <EligibilityBadge eligibility={item.eligibility} />
        </div>
      </div>

      <div className="mt-5 border-t border-[var(--divider)] pt-4">
        <ExplanationLists strengths={item.strengths} gaps={item.gaps} />
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-2">
        <ShortlistButton
          profileId={profileId}
          opportunityId={opportunity.id}
          shortlisted={item.shortlisted ?? false}
        />
        <Button asChild variant="ghost" size="sm">
          <Link
            to="/opportunities/$opportunityId"
            params={{ opportunityId: opportunity.id }}
          >
            View details
          </Link>
        </Button>
        <button
          type="button"
          onClick={onToggle}
          aria-expanded={expanded}
          className="ml-auto inline-flex items-center gap-1.5 rounded-md px-2 py-1.5 text-xs font-semibold text-[var(--ink-secondary)] transition hover:text-[var(--ink)]"
        >
          {expanded ? 'Hide score breakdown' : 'Why this score?'}
          <ChevronDown
            aria-hidden
            className={`size-3.5 transition-transform duration-200 ${expanded ? 'rotate-180' : ''}`}
          />
        </button>
      </div>

      <div
        className={`grid transition-[grid-template-rows,opacity] duration-300 ease-out ${
          expanded
            ? 'mt-4 grid-rows-[1fr] opacity-100'
            : 'grid-rows-[0fr] opacity-0'
        }`}
      >
        <div className="overflow-hidden">
          <div className="grid gap-6 border-t border-[var(--divider)] pt-5 sm:grid-cols-2">
            <div>
              <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-[var(--ink-secondary)]">
                Six-part score · cosine {item.cosine_similarity.toFixed(3)}
              </p>
              <DimensionBars breakdown={item.score_breakdown} />
            </div>
            <div>
              <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-[var(--ink-secondary)]">
                Eligibility evidence
              </p>
              <EligibilityChecks eligibility={item.eligibility} />
            </div>
          </div>
        </div>
      </div>
    </article>
  )
}
