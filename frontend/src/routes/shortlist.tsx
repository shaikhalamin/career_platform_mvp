import { createFileRoute, Link } from '@tanstack/react-router'
import { CalendarClock, Heart, MapPin, Quote } from 'lucide-react'

import { Button } from '#/components/ui/button'
import { PageHeader } from '#/components/page-header'
import { EmptyState } from '#/components/empty-state'
import { ListRowsSkeleton } from '#/components/skeletons'
import { useActiveProfile } from '#/lib/active-profile'
import { ShortlistButton } from '#/components/shortlist-button'
import { useListShortlistApiV1ShortlistGet } from '#/gen/queries/shortlist/useListShortlistApiV1ShortlistGet'

export const Route = createFileRoute('/shortlist')({
  component: ShortlistPage,
})

function ShortlistPage() {
  const { activeProfileId } = useActiveProfile()

  if (activeProfileId === null) {
    return (
      <main className="page-wrap py-16">
        <EmptyState
          icon={Heart}
          title="No active profile"
          description="Shortlists belong to a profile — pick one to see saved opportunities."
          actions={
            <Button asChild>
              <Link to="/profiles">Choose a profile</Link>
            </Button>
          }
        />
      </main>
    )
  }

  return <ShortlistList profileId={activeProfileId} />
}

function ShortlistList({ profileId }: { profileId: number }) {
  const query = useListShortlistApiV1ShortlistGet({
    query: { profile_id: profileId },
  })
  const items = query.data?.data ?? []

  return (
    <main className="page-wrap py-10">
      <PageHeader
        eyebrow="Wishlist"
        title="Shortlisted opportunities"
        description="Saved roles for this profile — match scores stay current because they're recomputed from your live profile."
      />

      {query.isPending ? (
        <ListRowsSkeleton count={3} />
      ) : items.length === 0 ? (
        <EmptyState
          icon={Heart}
          title="Nothing saved yet"
          description="Shortlist roles that interest you and they'll wait here — scores and eligibility stay up to date with your profile."
          actions={
            <>
              <Button asChild>
                <Link to="/recommendations">Browse recommendations</Link>
              </Button>
              <Button asChild variant="outline">
                <Link to="/opportunities">Search the catalogue</Link>
              </Button>
            </>
          }
        />
      ) : (
        <div className="space-y-4">
          {items.map((item) => (
            <article
              key={item.id}
              className="panel-card is-interactive p-5 sm:p-6"
            >
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div className="min-w-0">
                  <Link
                    to="/opportunities/$opportunityId"
                    params={{ opportunityId: item.opportunity.id }}
                    className="text-base font-semibold text-[var(--ink)] no-underline hover:underline"
                  >
                    {item.opportunity.title}
                  </Link>
                  <div className="mt-1.5 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-[var(--ink-secondary)]">
                    <span className="font-medium">
                      {item.opportunity.organisation}
                    </span>
                    <span className="inline-flex items-center gap-1">
                      <MapPin
                        aria-hidden
                        className="size-3 text-[var(--ink-tertiary)]"
                      />
                      {item.opportunity.country}
                    </span>
                    <span className="inline-flex items-center gap-1">
                      <CalendarClock
                        aria-hidden
                        className="size-3 text-[var(--ink-tertiary)]"
                      />
                      saved {new Date(item.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  {item.note && (
                    <p className="mt-3 flex gap-2 rounded-lg bg-[var(--canvas-soft)] py-2 pr-3 pl-2.5 text-xs leading-relaxed text-[var(--ink-secondary)]">
                      <Quote
                        aria-hidden
                        className="mt-0.5 size-3 shrink-0 text-[var(--ink-tertiary)]"
                      />
                      {item.note}
                    </p>
                  )}
                </div>
                <ShortlistButton
                  profileId={profileId}
                  opportunityId={item.opportunity.id}
                  shortlisted
                />
              </div>
            </article>
          ))}
        </div>
      )}
    </main>
  )
}
