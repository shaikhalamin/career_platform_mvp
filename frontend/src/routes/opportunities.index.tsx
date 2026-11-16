import { useState } from 'react'
import { createFileRoute, Link } from '@tanstack/react-router'

import { useActiveProfile } from '#/lib/active-profile'
import { ShortlistButton } from '#/components/shortlist-button'
import { useListOpportunitiesApiV1OpportunitiesGet } from '#/gen/queries/opportunities/useListOpportunitiesApiV1OpportunitiesGet'
import { useGetTaxonomyApiV1MetaTaxonomyGet } from '#/gen/queries/meta/useGetTaxonomyApiV1MetaTaxonomyGet'

export const Route = createFileRoute('/opportunities/')({
  component: OpportunitiesPage,
})

const EMPLOYMENT_LABELS: Record<string, string> = {
  full_time: 'Full-time',
  internship: 'Internship',
  contract: 'Contract',
  part_time: 'Part-time',
}

function OpportunitiesPage() {
  const { activeProfileId } = useActiveProfile()
  const [country, setCountry] = useState('')
  const [employmentType, setEmploymentType] = useState('')
  const [search, setSearch] = useState('')

  const taxonomyQuery = useGetTaxonomyApiV1MetaTaxonomyGet()
  const countries =
    taxonomyQuery.data?.data?.countries.map((entry) => entry.name) ?? []

  const listQuery = useListOpportunitiesApiV1OpportunitiesGet({
    query: {
      page: 1,
      page_size: 50,
      ...(country ? { country } : {}),
      ...(employmentType ? { employment_type: employmentType } : {}),
      ...(search.trim() ? { search: search.trim() } : {}),
      ...(activeProfileId !== null ? { profile_id: activeProfileId } : {}),
    },
  })

  const opportunities = listQuery.data?.data ?? []
  const meta = listQuery.data?.meta
  const total =
    meta && typeof meta === 'object' && 'total_items' in meta
      ? Number(meta.total_items)
      : opportunities.length

  return (
    <main className="page-wrap py-10">
      <div className="mb-6">
        <p className="tier-eyebrow mb-2">Browse the opportunity catalogue</p>
        <h1 className="display-title m-0 text-3xl font-semibold tracking-tight text-[var(--ink)]">
          Opportunities
        </h1>
        <p className="mt-2 text-sm text-[var(--ink-secondary)]">
          {total} structured job and internship postings — requirements,
          languages and eligibility constraints in the open.
        </p>
      </div>

      <div className="panel-card mb-6 flex flex-wrap items-end gap-3 p-4">
        <label className="flex flex-1 flex-col gap-1 text-xs font-semibold text-[var(--ink-secondary)]">
          Search
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Role, organisation, city…"
            className="rounded-md border border-[var(--input-border)] bg-transparent px-3 py-2 text-sm font-normal text-[var(--ink)] outline-none focus:border-[var(--store-blue)]"
          />
        </label>
        <label className="flex flex-col gap-1 text-xs font-semibold text-[var(--ink-secondary)]">
          Country
          <select
            value={country}
            onChange={(e) => setCountry(e.target.value)}
            className="rounded-md border border-[var(--input-border)] bg-transparent px-3 py-2 text-sm font-normal"
          >
            <option value="">All countries</option>
            {countries.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1 text-xs font-semibold text-[var(--ink-secondary)]">
          Type
          <select
            value={employmentType}
            onChange={(e) => setEmploymentType(e.target.value)}
            className="rounded-md border border-[var(--input-border)] bg-transparent px-3 py-2 text-sm font-normal"
          >
            <option value="">All types</option>
            {Object.entries(EMPLOYMENT_LABELS).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>
      </div>

      {listQuery.isPending ? (
        <p className="text-sm text-[var(--ink-secondary)]">
          Loading opportunities…
        </p>
      ) : listQuery.isError ? (
        <p className="text-sm font-semibold text-red-600">
          Failed to load opportunities — is the backend running on port 8000?
        </p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {opportunities.map((opportunity) => (
            <article
              key={opportunity.id}
              className="panel-card flex flex-col p-5"
            >
              <div className="mb-1 flex items-start justify-between gap-3">
                <Link
                  to="/opportunities/$opportunityId"
                  params={{ opportunityId: opportunity.id }}
                  className="text-base font-semibold text-[var(--ink)] no-underline hover:underline"
                >
                  {opportunity.title}
                </Link>
                {opportunity.eligibility.local_work_authorization_required && (
                  <span
                    className="shrink-0 rounded-full border border-[color-mix(in_oklab,var(--tier-orange)_40%,transparent)] px-2 py-0.5 text-[10px] font-bold text-[var(--tier-orange)]"
                    title="Requires existing local work authorisation"
                  >
                    LOCAL HIRE
                  </span>
                )}
              </div>
              <p className="m-0 text-xs text-[var(--ink-secondary)]">
                {opportunity.organisation} ·{' '}
                {opportunity.city ? `${opportunity.city}, ` : ''}
                {opportunity.country} ·{' '}
                {EMPLOYMENT_LABELS[opportunity.employment_type] ??
                  opportunity.employment_type}
              </p>
              <p className="mt-2 line-clamp-2 text-xs text-[var(--ink-secondary)]">
                {opportunity.description}
              </p>
              <div className="mt-2 flex flex-wrap gap-1">
                {(opportunity.skills.required ?? [])
                  .slice(0, 5)
                  .map((skill) => (
                    <span
                      key={skill}
                      className="rounded-sm bg-[var(--fog)] px-1.5 py-0.5 text-[10px] text-[var(--ink-secondary)]"
                    >
                      {skill}
                    </span>
                  ))}
              </div>
              <div className="mt-3 flex flex-wrap items-center gap-2 border-t border-[var(--divider)] pt-3 text-xs text-[var(--ink-tertiary)]">
                {opportunity.experience.min_years}–
                {opportunity.experience.max_years} yrs ·{' '}
                {opportunity.education.min_level} ·{' '}
                {Object.keys(opportunity.languages_required).join(', ') ||
                  'No language requirement'}
                <div className="ml-auto">
                  <ShortlistButton
                    profileId={activeProfileId}
                    opportunityId={opportunity.id}
                    shortlisted={opportunity.shortlisted ?? false}
                  />
                </div>
              </div>
            </article>
          ))}
          {opportunities.length === 0 && (
            <p className="text-sm text-[var(--ink-secondary)]">
              No opportunities match these filters.
            </p>
          )}
        </div>
      )}
    </main>
  )
}
