import { useMemo, useState } from 'react'
import { createFileRoute, Link } from '@tanstack/react-router'
import {
  Briefcase,
  CircleAlert,
  Clock3,
  MapPin,
  Search,
  SearchX,
  X,
} from 'lucide-react'

import { Badge } from '#/components/ui/badge'
import { Button } from '#/components/ui/button'
import { PageHeader } from '#/components/page-header'
import { EmptyState } from '#/components/empty-state'
import { CardGridSkeleton } from '#/components/skeletons'
import { SearchableSelect } from '#/components/ui/searchable-select'
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

/** Deterministic pastel per organisation for the avatar tile. */
const AVATAR_HUES = [197, 12, 150, 262, 33, 0, 45, 220]

function OrgAvatar({ organisation }: { organisation: string }) {
  const initials = organisation
    .split(/\s+/)
    .slice(0, 2)
    .map((word) => word.charAt(0).toUpperCase())
    .join('')
  const hue =
    AVATAR_HUES[
      organisation
        .split('')
        .reduce((sum, char) => sum + char.charCodeAt(0), 0) % AVATAR_HUES.length
    ]
  return (
    <span
      aria-hidden
      className="inline-flex size-10 shrink-0 items-center justify-center rounded-lg text-sm font-semibold"
      style={{
        backgroundColor: `oklch(0.93 0.04 ${hue})`,
        color: `oklch(0.45 0.11 ${hue})`,
      }}
    >
      {initials}
    </span>
  )
}

function OpportunitiesPage() {
  const { activeProfileId } = useActiveProfile()
  const [country, setCountry] = useState('')
  const [employmentType, setEmploymentType] = useState('')
  const [search, setSearch] = useState('')

  const taxonomyQuery = useGetTaxonomyApiV1MetaTaxonomyGet()
  const countryOptions = useMemo(
    () =>
      taxonomyQuery.data?.data?.countries.map((entry) => ({
        label: entry.name,
        value: entry.name,
        hint: entry.region,
        keywords: [entry.name.toLowerCase(), ...(entry.aliases ?? [])],
      })) ?? [],
    [taxonomyQuery.data],
  )

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

  const hasFilters = Boolean(country || employmentType || search.trim())
  const clearFilters = () => {
    setCountry('')
    setEmploymentType('')
    setSearch('')
  }

  const filterSelectClass =
    'rounded-lg border border-[var(--input-border)] bg-[var(--canvas)] px-3 py-2 text-sm text-[var(--ink)]'

  return (
    <main className="page-wrap py-10">
      <PageHeader
        eyebrow="Browse the opportunity catalogue"
        title="Opportunities"
        description={`${total} structured job and internship postings — requirements, languages and eligibility constraints in the open.`}
      />

      {/* Filter bar */}
      <div className="panel-card mb-6 flex flex-wrap items-end gap-3 p-4">
        <label className="flex min-w-56 flex-1 flex-col gap-1.5">
          <span className="text-xs font-medium text-[var(--ink-secondary)]">
            Search
          </span>
          <span className="relative">
            <Search
              aria-hidden
              className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-[var(--ink-tertiary)]"
            />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Role, organisation, city…"
              className="w-full rounded-lg border border-[var(--input-border)] bg-[var(--canvas)] py-2 pr-3 pl-9 text-sm text-[var(--ink)] outline-none placeholder:text-[var(--ink-tertiary)] focus:border-[var(--ring)] focus:ring-[3px] focus:ring-ring/30"
            />
          </span>
        </label>
        <div className="flex flex-col gap-1.5">
          <span className="text-xs font-medium text-[var(--ink-secondary)]">
            Country
          </span>
          <SearchableSelect
            value={country}
            onValueChange={setCountry}
            options={countryOptions}
            placeholder="All countries"
            searchPlaceholder="Search countries by name or code…"
            clearLabel="All countries"
            emptyMessage="No country matches that search."
          />
        </div>
        <label className="flex flex-col gap-1.5">
          <span className="text-xs font-medium text-[var(--ink-secondary)]">
            Type
          </span>
          <select
            value={employmentType}
            onChange={(e) => setEmploymentType(e.target.value)}
            className={filterSelectClass}
          >
            <option value="">All types</option>
            {Object.entries(EMPLOYMENT_LABELS).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>
        {hasFilters && (
          <Button variant="ghost" size="sm" onClick={clearFilters}>
            <X aria-hidden />
            Clear filters
          </Button>
        )}
      </div>

      {listQuery.isPending ? (
        <CardGridSkeleton className="md:grid-cols-2" count={6} />
      ) : listQuery.isError ? (
        <div
          role="alert"
          className="flex items-center gap-3 rounded-xl border border-[color-mix(in_oklab,var(--error)_30%,transparent)] bg-[color-mix(in_oklab,var(--error)_6%,transparent)] px-5 py-4 text-sm font-medium text-[var(--error)]"
        >
          <CircleAlert aria-hidden className="size-5 shrink-0" />
          Failed to load opportunities — is the backend running on port 8000?
        </div>
      ) : opportunities.length === 0 ? (
        <EmptyState
          icon={SearchX}
          title="No opportunities match"
          description={
            hasFilters
              ? 'Try widening your search or clearing the filters — the catalogue covers 50 roles across all regions.'
              : 'The catalogue is empty — check back soon.'
          }
          actions={
            hasFilters ? (
              <Button variant="outline" onClick={clearFilters}>
                Clear filters
              </Button>
            ) : undefined
          }
        />
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {opportunities.map((opportunity) => (
            <article
              key={opportunity.id}
              className="panel-card is-interactive flex flex-col p-5"
            >
              <div className="mb-3 flex items-start gap-3">
                <OrgAvatar organisation={opportunity.organisation} />
                <div className="min-w-0 flex-1">
                  <div className="flex items-start justify-between gap-2">
                    <Link
                      to="/opportunities/$opportunityId"
                      params={{ opportunityId: opportunity.id }}
                      className="text-base leading-snug font-semibold text-[var(--ink)] no-underline hover:underline"
                    >
                      {opportunity.title}
                    </Link>
                    {opportunity.eligibility
                      .local_work_authorization_required && (
                      <Badge
                        variant="warning-outline"
                        className="shrink-0"
                        title="Requires existing local work authorisation"
                      >
                        Local hire only
                      </Badge>
                    )}
                  </div>
                  <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-[var(--ink-secondary)]">
                    <span className="font-medium">
                      {opportunity.organisation}
                    </span>
                    <span className="inline-flex items-center gap-1">
                      <MapPin
                        aria-hidden
                        className="size-3 text-[var(--ink-tertiary)]"
                      />
                      {opportunity.city ? `${opportunity.city}, ` : ''}
                      {opportunity.country}
                    </span>
                    <span className="inline-flex items-center gap-1">
                      <Briefcase
                        aria-hidden
                        className="size-3 text-[var(--ink-tertiary)]"
                      />
                      {EMPLOYMENT_LABELS[opportunity.employment_type] ??
                        opportunity.employment_type}
                    </span>
                  </div>
                </div>
              </div>
              <p className="m-0 line-clamp-2 text-sm leading-relaxed text-[var(--ink-secondary)]">
                {opportunity.description}
              </p>
              <div className="mt-3 flex flex-wrap gap-1.5">
                {(opportunity.skills.required ?? [])
                  .slice(0, 5)
                  .map((skill) => (
                    <Badge
                      key={skill}
                      variant="secondary"
                      className="px-2 py-0 font-normal"
                    >
                      {skill}
                    </Badge>
                  ))}
              </div>
              <div className="mt-auto flex flex-wrap items-center gap-2 border-t border-[var(--divider)] pt-4 text-xs text-[var(--ink-tertiary)]">
                <span className="inline-flex items-center gap-1">
                  <Clock3 aria-hidden className="size-3" />
                  {opportunity.experience.min_years}–
                  {opportunity.experience.max_years} yrs
                </span>
                <span aria-hidden>·</span>
                <span>{opportunity.education.min_level}</span>
                <span aria-hidden>·</span>
                <span>
                  {Object.keys(opportunity.languages_required).join(', ') ||
                    'No language requirement'}
                </span>
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
        </div>
      )}
    </main>
  )
}
