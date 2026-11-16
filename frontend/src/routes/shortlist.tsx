import { createFileRoute, Link } from '@tanstack/react-router'

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
        <div className="panel-card mx-auto max-w-lg p-8 text-center">
          <h1 className="display-title m-0 text-2xl">No active profile</h1>
          <p className="mt-3 text-sm text-[var(--ink-secondary)]">
            Shortlists belong to a profile — pick one to see saved
            opportunities.
          </p>
          <Link to="/profiles" className="pill-primary mt-6">
            Choose a profile
          </Link>
        </div>
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
      <div className="mb-6">
        <p className="tier-eyebrow mb-2">Wishlist</p>
        <h1 className="display-title m-0 text-3xl font-semibold tracking-tight text-[var(--ink)]">
          Shortlisted opportunities
        </h1>
        <p className="mt-2 text-sm text-[var(--ink-secondary)]">
          Saved roles for this profile — match scores stay current because
          they're recomputed from your live profile.
        </p>
      </div>

      {query.isPending ? (
        <p className="text-sm text-[var(--ink-secondary)]">
          Loading shortlist…
        </p>
      ) : items.length === 0 ? (
        <div className="panel-card p-10 text-center text-sm text-[var(--ink-secondary)]">
          Nothing saved yet — shortlist roles from{' '}
          <Link to="/recommendations" className="underline">
            your recommendations
          </Link>{' '}
          or the{' '}
          <Link to="/opportunities" className="underline">
            catalogue
          </Link>
          .
        </div>
      ) : (
        <div className="space-y-4">
          {items.map((item) => (
            <article key={item.id} className="panel-card p-5">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <Link
                    to="/opportunities/$opportunityId"
                    params={{ opportunityId: item.opportunity.id }}
                    className="text-base font-semibold text-[var(--ink)] no-underline hover:underline"
                  >
                    {item.opportunity.title}
                  </Link>
                  <p className="m-0 text-xs text-[var(--ink-secondary)]">
                    {item.opportunity.organisation} · {item.opportunity.country}{' '}
                    · saved {new Date(item.created_at).toLocaleDateString()}
                  </p>
                  {item.note && (
                    <p className="mt-2 rounded-md bg-[var(--fog)] px-3 py-1.5 text-xs text-[var(--ink-secondary)]">
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
