import { createFileRoute, Link } from '@tanstack/react-router'

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
        <p className="text-sm text-[var(--ink-secondary)]">
          Loading opportunity…
        </p>
      </main>
    )
  }

  if (detailQuery.isError || !detailQuery.data.data) {
    return (
      <main className="page-wrap py-10">
        <p className="text-sm font-semibold text-red-600">
          Opportunity {opportunityId} not found.
        </p>
      </main>
    )
  }

  const opportunity = detailQuery.data.data
  const match = matchQuery.data?.data

  return (
    <main className="page-wrap py-10">
      <Link
        to="/opportunities"
        className="text-xs font-semibold text-[var(--link-blue)] hover:underline"
      >
        ← All opportunities
      </Link>

      <div className="mt-3 flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="tier-eyebrow mb-1">{opportunity.id}</p>
          <h1 className="display-title m-0 text-3xl font-semibold tracking-tight text-[var(--ink)]">
            {opportunity.title}
          </h1>
          <p className="mt-1 text-sm text-[var(--ink-secondary)]">
            {opportunity.organisation} ·{' '}
            {opportunity.city ? `${opportunity.city}, ` : ''}
            {opportunity.country} ·{' '}
            {EMPLOYMENT_LABELS[opportunity.employment_type] ??
              opportunity.employment_type}
          </p>
        </div>
        <ShortlistButton
          profileId={activeProfileId}
          opportunityId={opportunity.id}
          shortlisted={match?.shortlisted ?? false}
          size="sm"
        />
      </div>

      <p className="mt-4 max-w-3xl text-sm leading-relaxed text-[var(--ink-secondary)]">
        {opportunity.description}
      </p>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <section className="panel-card p-6">
          <h2 className="m-0 mb-4 text-base font-semibold text-[var(--ink)]">
            Requirements
          </h2>
          <dl className="m-0 grid grid-cols-[auto_1fr] gap-x-6 gap-y-3 text-sm">
            <dt className="font-semibold text-[var(--ink-secondary)]">
              Skills (required)
            </dt>
            <dd className="m-0 text-[var(--ink)]">
              {(opportunity.skills.required ?? []).join(', ') || '—'}
            </dd>
            <dt className="font-semibold text-[var(--ink-secondary)]">
              Skills (nice to have)
            </dt>
            <dd className="m-0 text-[var(--ink)]">
              {(opportunity.skills.optional ?? []).join(', ') || '—'}
            </dd>
            <dt className="font-semibold text-[var(--ink-secondary)]">
              Experience
            </dt>
            <dd className="m-0 text-[var(--ink)]">
              {opportunity.experience.min_years}–
              {opportunity.experience.max_years} years
              {(() => {
                const areas = opportunity.experience.areas ?? []
                return areas.length > 0 ? ` · areas: ${areas.join(', ')}` : null
              })()}
            </dd>
            <dt className="font-semibold text-[var(--ink-secondary)]">
              Education
            </dt>
            <dd className="m-0 text-[var(--ink)]">
              {opportunity.education.min_level}
              {(() => {
                const fields = opportunity.education.relevant_fields ?? []
                return fields.length > 0
                  ? ` (fields: ${fields.join(', ')})`
                  : null
              })()}
            </dd>
            <dt className="font-semibold text-[var(--ink-secondary)]">
              Languages
            </dt>
            <dd className="m-0 text-[var(--ink)]">
              {Object.entries(opportunity.languages_required)
                .map(([language, level]) => `${language} (${level})`)
                .join(', ') || 'None stated'}
            </dd>
            <dt className="font-semibold text-[var(--ink-secondary)]">
              Career tracks
            </dt>
            <dd className="m-0 text-[var(--ink)]">
              {opportunity.career_tracks.join(', ') || '—'}
            </dd>
            <dt className="font-semibold text-[var(--ink-secondary)]">
              Eligibility
            </dt>
            <dd className="m-0 text-[var(--ink)]">
              <ul className="m-0 list-none space-y-1 p-0 text-xs">
                {opportunity.eligibility.local_work_authorization_required && (
                  <li>• Requires existing local work authorisation</li>
                )}
                {(() => {
                  const citizenship =
                    opportunity.eligibility.citizenship_required ?? []
                  return citizenship.length > 0 ? (
                    <li>• Restricted to {citizenship.join(' / ')} citizens</li>
                  ) : null
                })()}
                {opportunity.eligibility.enrollment_required && (
                  <li>• Open to currently enrolled students only</li>
                )}
                {opportunity.eligibility.strict_language && (
                  <li>
                    • Language requirements are mandatory (not a scored gap)
                  </li>
                )}
                {opportunity.eligibility.strict_education && (
                  <li>• Education requirement is strictly enforced</li>
                )}
                {opportunity.eligibility.strict_experience && (
                  <li>• Experience window is strictly enforced</li>
                )}
                {!opportunity.eligibility.local_work_authorization_required &&
                  !(
                    (opportunity.eligibility.citizenship_required ?? [])
                      .length > 0
                  ) &&
                  !opportunity.eligibility.enrollment_required &&
                  !opportunity.eligibility.strict_language &&
                  !opportunity.eligibility.strict_education &&
                  !opportunity.eligibility.strict_experience && (
                    <li>• No hard constraints declared</li>
                  )}
              </ul>
            </dd>
          </dl>
        </section>

        <section className="panel-card p-6">
          <h2 className="m-0 mb-4 text-base font-semibold text-[var(--ink)]">
            Your match
          </h2>
          {activeProfileId === null ? (
            <p className="m-0 text-sm text-[var(--ink-secondary)]">
              <Link to="/profiles" className="underline">
                Pick a profile
              </Link>{' '}
              to see how well you match this role.
            </p>
          ) : matchQuery.isPending ? (
            <p className="m-0 text-sm text-[var(--ink-secondary)]">
              Evaluating match…
            </p>
          ) : match ? (
            <div className="space-y-5">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <ScoreMeter score={match.total_score} max={match.max_score} />
                <EligibilityBadge eligibility={match.eligibility} />
              </div>
              <DimensionBars breakdown={match.score_breakdown} />
              <ExplanationLists strengths={match.strengths} gaps={match.gaps} />
              <div>
                <p className="mb-2 text-xs font-bold uppercase tracking-wider text-[var(--ink-secondary)]">
                  Eligibility evidence
                </p>
                <EligibilityChecks eligibility={match.eligibility} />
              </div>
              <DisclaimerNote text={match.disclaimer} />
            </div>
          ) : (
            <p className="m-0 text-sm font-semibold text-red-600">
              Failed to evaluate match.
            </p>
          )}
        </section>
      </div>
    </main>
  )
}
