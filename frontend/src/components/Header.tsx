import { Link, useNavigate } from '@tanstack/react-router'

import ThemeToggle from './ThemeToggle'
import { useActiveProfile } from '#/lib/active-profile'
import { useListProfilesApiV1ProfilesGet } from '#/gen/queries/profiles/useListProfilesApiV1ProfilesGet'

export default function Header() {
  const { activeProfileId, setActiveProfile } = useActiveProfile()
  const navigate = useNavigate()
  const profilesQuery = useListProfilesApiV1ProfilesGet({
    query: { page: 1, page_size: 100 },
  })
  const profiles = profilesQuery.data?.data ?? []
  const activeProfile = profiles.find(
    (profile) => profile.id === activeProfileId,
  )

  return (
    <header className="sticky top-0 z-50 border-b border-[var(--hairline)] bg-[var(--canvas)] px-4">
      <nav className="page-wrap flex min-h-16 flex-wrap items-center gap-x-3 gap-y-2 py-2">
        <h2 className="m-0 flex-shrink-0 text-base font-semibold tracking-tight">
          <Link
            to="/"
            className="inline-flex items-center gap-2 px-1 text-base font-semibold tracking-tight text-[var(--ink)] no-underline"
          >
            <span
              aria-hidden
              className="inline-block size-2 rounded-full bg-[var(--store-blue)]"
            />
            PathPilot
          </Link>
        </h2>

        <div className="order-3 flex w-full flex-wrap items-center gap-x-4 gap-y-1 pb-1 sm:order-none sm:w-auto sm:flex-nowrap sm:pb-0">
          <Link
            to="/"
            className="nav-link"
            activeProps={{ className: 'nav-link is-active' }}
          >
            Home
          </Link>
          <Link
            to="/recommendations"
            className="nav-link"
            activeProps={{ className: 'nav-link is-active' }}
          >
            Recommendations
          </Link>
          <Link
            to="/opportunities"
            className="nav-link"
            activeProps={{ className: 'nav-link is-active' }}
          >
            Opportunities
          </Link>
          <Link
            to="/shortlist"
            className="nav-link"
            activeProps={{ className: 'nav-link is-active' }}
          >
            Shortlist
          </Link>
          <Link
            to="/about"
            className="nav-link"
            activeProps={{ className: 'nav-link is-active' }}
          >
            How it works
          </Link>
        </div>

        <div className="ml-auto flex items-center gap-2">
          <label className="hidden items-center gap-2 sm:flex">
            <span className="sr-only">Active profile</span>
            <select
              value={activeProfileId ?? ''}
              onChange={(e) => {
                const value = e.target.value
                setActiveProfile(value ? Number(value) : null)
                void navigate({ to: '/recommendations' })
              }}
              className="max-w-44 truncate rounded-full border border-[var(--input-border)] bg-transparent px-3 py-1.5 text-xs text-[var(--ink)]"
            >
              <option value="">No profile</option>
              {profiles.map((profile) => (
                <option key={profile.id} value={profile.id}>
                  {profile.name}
                </option>
              ))}
            </select>
          </label>
          {activeProfile && (
            <Link
              to="/profiles/$profileId/edit"
              params={{ profileId: String(activeProfile.id) }}
              className="hidden rounded-full bg-[var(--fog)] px-3 py-1.5 text-xs font-semibold text-[var(--ink)] no-underline hover:bg-[var(--store-blue-tint)] md:block"
            >
              Edit profile
            </Link>
          )}
          <ThemeToggle />
        </div>
      </nav>
    </header>
  )
}
