import { createFileRoute, Link } from '@tanstack/react-router'
import {
  ArrowLeft,
  Briefcase,
  Clock3,
  GraduationCap,
  Languages,
  MapPin,
  Route as RouteIcon,
  ShieldAlert,
  Wrench,
} from 'lucide-react'

import { Badge } from '#/components/ui/badge'
import {
  DisclaimerNote,
  DimensionBars,
  EligibilityBadge,
  EligibilityChecks,
  ExplanationLists,
} from '#/components/match'
import { ScoreGauge } from '#/components/score-gauge'
import { DetailPageSkeleton } from '#/components/skeletons'
import { ShortlistButton } from '#/components/shortlist-button'
import { useActiveProfile } from '#/lib/active-profile'
import { useGetOpportunityApiV1OpportunitiesOpportunityIdGet } from '#/gen/queries/opportunities/useGetOpportunityApiV1OpportunitiesOpportunityIdGet'
import { useMatchOpportunityApiV1OpportunitiesOpportunityIdMatchGet } from '#/gen/queries/opportunities/useMatchOpportunityApiV1OpportunitiesOpportunityIdMatchGet'

export const Route = createFileRoute('/opportunities/$opportunityId')({
  component: OpportunityDetailPage,
})

const EMPLOYMENT_LABELS: Record<string, string> = {
  full_time: 'Full-time',
  internship: 'Internship',
  contract: 'Contract',
  part_time: 'Part-time',
}

function RequirementRow({
  icon: Icon,
  label,
  children,
}: {
  icon: typeof Wrench
  label: string
  children: React.ReactNode
}) {
  return (
    <div className="flex gap-3.5">
      <span
        aria-hidden
        className="mt-0.5 inline-flex size-8 shrink-0 items-center justify-center rounded-lg bg-[var(--panel)] text-[var(--ink-secondary)]"
      >
        <Icon className="size-4" />
      </span>
      <div className="min-w-0">
        <dt className="text-xs font-medium tracking-wide text-[var(--ink-tertiary)] uppercase">
          {label}
        </dt>
        <dd className="m-0 mt-1 text-sm leading-relaxed text-[var(--ink)]">
          {children}
        </dd>
      </div>
    </div>
  )
}

function OpportunityDetailPage() {
  const { opportunityId } = Route.useParams()
  const { activeProfileId } = useActiveProfile()

  const detailQuery = useGetOpportunityApiV1OpportunitiesOpportunityIdGet({
    path: { opportunity_id: opportunityId },
  })

  const matchQuery = useMatchOpportunityApiV1OpportunitiesOpportunityIdMatchGet(
    {
      path: { opportunity_id: opportunityId },
      query: { profile_id: activeProfileId ?? 0 },
    },
    // No active profile -> skip the request entirely (0 is never sent).
    { query: { enabled: activeProfileId !== null } },
  )

  if (detailQuery.isPending) {
    return (
      <main className="page-wrap py-10">
        <DetailPageSkeleton />
      </main>
    )
  }

  if (detailQuery.isError || !detailQuery.data.data) {
    return (
      <main className="page-wrap py-10">
        <Link
          to="/opportunities"
          className="inline-flex items-center gap-1.5 text-sm font-medium no-underline hover:underline"
        >
          <ArrowLeft aria-hidden className="size-4" />
          All opportunities
        </Link>
        <div
          role="alert"
          className="mt-6 rounded-xl border border-[color-mix(in_oklab,var(--error)_30%,transparent)] bg-[color-mix(in_oklab,var(--error)_6%,transparent)] px-5 py-4 text-sm font-medium text-[var(--error)]"
        >
          Opportunity {opportunityId} not found.
        </div>
      </main>
    )
  }

  const opportunity = detailQuery.data.data
  const match = matchQuery.data?.data

  const constraints: string[] = []
  if (opportunity.eligibility.local_work_authorization_required) {
    constraints.push('Requires existing local work authorisation')
  }
  const citizenship = opportunity.eligibility.citizenship_required ?? []
  if (citizenship.length > 0) {
    constraints.push(`Restricted to ${citizenship.join(' / ')} citizens`)
  }
  if (opportunity.eligibility.enrollment_required) {
    constraints.push('Open to currently enrolled students only')
  }
  if (opportunity.eligibility.strict_language) {
    constraints.push('Language requirements are mandatory (not a scored gap)')
  }
  if (opportunity.eligibility.strict_education) {
    constraints.push('Education requirement is strictly enforced')
  }
  if (opportunity.eligibility.strict_experience) {
    constraints.push('Experience window is strictly enforced')
  }

  return (
    <main className="page-wrap py-10">
      <Link
        to="/opportunities"
        className="inline-flex items-center gap-1.5 text-sm font-medium no-underline hover:underline"
      >
        <ArrowLeft aria-hidden className="size-4" />
        All opportunities
      </Link>

      <div className="mt-5 flex flex-wrap items-start justify-between gap-4">
        <div className="flex min-w-0 gap-4">
          <span
            aria-hidden
            className="inline-flex size-12 shrink-0 items-center justify-center rounded-xl bg-[var(--primary)] text-lg font-semibold text-[var(--on-primary)]"
          >
            {opportunity.organisation
              .split(/\s+/)
              .slice(0, 2)
              .map((word) => word.charAt(0).toUpperCase())
              .join('')}
          </span>
          <div className="min-w-0">
            <p className="tier-eyebrow mb-1.5">Opportunity #{opportunity.id}</p>
            <h1 className="display-title m-0 text-3xl tracking-tight">
              {opportunity.title}
            </h1>
            <div className="mt-2.5 flex flex-wrap items-center gap-x-4 gap-y-1.5 text-sm text-[var(--ink-secondary)]">
              <span className="font-medium">{opportunity.organisation}</span>
              <span className="inline-flex items-center gap-1.5">
                <MapPin
                  aria-hidden
                  className="size-3.5 text-[var(--ink-tertiary)]"
                />
                {opportunity.city ? `${opportunity.city}, ` : ''}
                {opportunity.country}
              </span>
              <span className="inline-flex items-center gap-1.5">
                <Briefcase
                  aria-hidden
                  className="size-3.5 text-[var(--ink-tertiary)]"
                />
                {EMPLOYMENT_LABELS[opportunity.employment_type] ??
                  opportunity.employment_type}
              </span>
              <span className="inline-flex items-center gap-1.5">
                <Clock3
                  aria-hidden
                  className="size-3.5 text-[var(--ink-tertiary)]"
                />
                {opportunity.experience.min_years}–
                {opportunity.experience.max_years} yrs
              </span>
            </div>
          </div>
        </div>
        <ShortlistButton
          profileId={activeProfileId}
          opportunityId={opportunity.id}
          shortlisted={match?.shortlisted ?? false}
          size="sm"
        />
      </div>

      <p className="mt-6 max-w-3xl text-base leading-relaxed text-[var(--ink-secondary)]">
        {opportunity.description}
      </p>

      <div className="mt-10 grid items-start gap-6 lg:grid-cols-2">
        <section className="panel-card p-6">
          <h2 className="m-0 mb-6 text-lg font-semibold tracking-tight text-[var(--ink)]">
            Requirements
          </h2>
          <dl className="m-0 grid grid-cols-1 gap-6">
            <RequirementRow icon={Wrench} label="Skills (required)">
              {(opportunity.skills.required ?? []).join(', ') || '—'}
            </RequirementRow>
            <RequirementRow icon={Wrench} label="Skills (nice to have)">
              {(opportunity.skills.optional ?? []).join(', ') || '—'}
            </RequirementRow>
            <RequirementRow icon={Clock3} label="Experience">
              {opportunity.experience.min_years}–
              {opportunity.experience.max_years} years
              {(() => {
                const areas = opportunity.experience.areas ?? []
                return areas.length > 0 ? ` · areas: ${areas.join(', ')}` : null
              })()}
            </RequirementRow>
            <RequirementRow icon={GraduationCap} label="Education">
              {opportunity.education.min_level}
              {(() => {
                const fields = opportunity.education.relevant_fields ?? []
                return fields.length > 0
                  ? ` (fields: ${fields.join(', ')})`
                  : null
              })()}
            </RequirementRow>
            <RequirementRow icon={Languages} label="Languages">
              {Object.entries(opportunity.languages_required)
                .map(([language, level]) => `${language} (${level})`)
                .join(', ') || 'None stated'}
            </RequirementRow>
            <RequirementRow icon={RouteIcon} label="Career tracks">
              {opportunity.career_tracks.join(', ') || '—'}
            </RequirementRow>
            <RequirementRow icon={ShieldAlert} label="Hard constraints">
              {constraints.length > 0 ? (
                <ul className="m-0 flex list-none flex-col gap-2 p-0">
                  {constraints.map((constraint) => (
                    <li key={constraint} className="flex items-start gap-2">
                      <Badge
                        variant="warning"
                        className="mt-0.5 shrink-0 font-normal"
                      >
                        {constraint}
                      </Badge>
                    </li>
                  ))}
                </ul>
              ) : (
                'No hard constraints declared'
              )}
            </RequirementRow>
          </dl>
        </section>

        <section className="panel-card p-6">
          <h2 className="m-0 mb-6 text-lg font-semibold tracking-tight text-[var(--ink)]">
            Your match
          </h2>
          {activeProfileId === null ? (
            <p className="m-0 text-sm leading-relaxed text-[var(--ink-secondary)]">
              <Link to="/profiles" className="underline">
                Pick a profile
              </Link>{' '}
              to see how well you match this role.
            </p>
          ) : matchQuery.isPending ? (
            <div className="flex items-center gap-3 py-6 text-sm text-[var(--ink-secondary)]">
              <span
                className="inline-block size-5 animate-spin rounded-full border-2 border-[var(--divider)] border-t-[var(--primary)]"
                aria-hidden
              />
              Evaluating match…
            </div>
          ) : match ? (
            <div className="space-y-6">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <ScoreGauge score={match.total_score} max={match.max_score} />
                <EligibilityBadge eligibility={match.eligibility} />
              </div>
              <DimensionBars breakdown={match.score_breakdown} />
              <ExplanationLists strengths={match.strengths} gaps={match.gaps} />
              <div className="border-t border-[var(--divider)] pt-5">
                <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-[var(--ink-secondary)]">
                  Eligibility evidence
                </p>
                <EligibilityChecks eligibility={match.eligibility} />
              </div>
              <DisclaimerNote text={match.disclaimer} />
            </div>
          ) : (
            <div
              role="alert"
              className="rounded-lg border border-[color-mix(in_oklab,var(--error)_30%,transparent)] bg-[color-mix(in_oklab,var(--error)_6%,transparent)] px-4 py-3 text-sm font-medium text-[var(--error)]"
            >
              Failed to evaluate match.
            </div>
          )}
        </section>
      </div>
    </main>
  )
}
