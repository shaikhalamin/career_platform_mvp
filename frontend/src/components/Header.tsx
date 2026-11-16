import { useState } from 'react'
import { Link, useNavigate } from '@tanstack/react-router'
import { Compass, Menu, Pencil, UserRound, X } from 'lucide-react'

import ThemeToggle from './ThemeToggle'
import { useActiveProfile } from '#/lib/active-profile'
import { useListProfilesApiV1ProfilesGet } from '#/gen/queries/profiles/useListProfilesApiV1ProfilesGet'

const NAV_LINKS = [
  { to: '/', label: 'Home' },
  { to: '/recommendations', label: 'Recommendations' },
  { to: '/opportunities', label: 'Opportunities' },
  { to: '/shortlist', label: 'Shortlist' },
  { to: '/about', label: 'How it works' },
] as const

export default function Header() {
  const { activeProfileId, setActiveProfile } = useActiveProfile()
  const navigate = useNavigate()
  const [menuOpen, setMenuOpen] = useState(false)
  const profilesQuery = useListProfilesApiV1ProfilesGet({
    query: { page: 1, page_size: 100 },
  })
  const profiles = profilesQuery.data?.data ?? []
  const activeProfile = profiles.find(
    (profile) => profile.id === activeProfileId,
  )

  const profileSelect = (
    <label className="flex items-center gap-2">
      <span className="sr-only">Active profile</span>
      <UserRound aria-hidden className="size-4 text-[var(--ink-tertiary)]" />
      <select
        value={activeProfileId ?? ''}
        onChange={(e) => {
          const value = e.target.value
          setActiveProfile(value ? Number(value) : null)
          void navigate({ to: '/recommendations' })
        }}
        className="max-w-44 truncate rounded-full border border-[var(--input-border)] bg-[var(--canvas)] py-1.5 pr-7 pl-3 text-xs font-medium text-[var(--ink)]"
      >
        <option value="">No profile</option>
        {profiles.map((profile) => (
          <option key={profile.id} value={profile.id}>
            {profile.name}
          </option>
        ))}
      </select>
    </label>
  )

  return (
    <header className="sticky top-0 z-50 border-b border-[var(--divider)] bg-[color-mix(in_oklab,var(--canvas)_85%,transparent)] backdrop-blur-md">
      <nav className="page-wrap flex min-h-16 items-center gap-x-6 py-2">
        <h2 className="m-0 flex-shrink-0 text-base font-semibold tracking-tight">
          <Link
            to="/"
            className="inline-flex items-center gap-2.5 text-base font-semibold tracking-tight text-[var(--ink)] no-underline"
          >
            <span
              aria-hidden
              className="inline-flex size-7 items-center justify-center rounded-lg bg-[var(--primary)] text-[var(--on-primary)]"
            >
              <Compass className="size-4" />
            </span>
            PathPilot
          </Link>
        </h2>

        <div className="hidden flex-wrap items-center gap-x-5 gap-y-1 md:flex">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className="nav-link"
              activeProps={{ className: 'nav-link is-active' }}
            >
              {link.label}
            </Link>
          ))}
        </div>

        <div className="ml-auto flex items-center gap-2.5">
          <div className="hidden items-center gap-2.5 lg:flex">
            {profileSelect}
            {activeProfile && (
              <Link
                to="/profiles/$profileId/edit"
                params={{ profileId: String(activeProfile.id) }}
                className="inline-flex items-center gap-1.5 rounded-full bg-[var(--panel)] px-3 py-1.5 text-xs font-medium text-[var(--ink)] no-underline hover:bg-[var(--primary-tint)]"
              >
                <Pencil aria-hidden className="size-3" />
                Edit profile
              </Link>
            )}
          </div>
          <ThemeToggle />
          <button
            type="button"
            className="inline-flex size-9 items-center justify-center rounded-lg text-[var(--ink-secondary)] transition hover:bg-[var(--panel)] hover:text-[var(--ink)] md:hidden"
            aria-expanded={menuOpen}
            aria-controls="mobile-nav"
            aria-label={menuOpen ? 'Close menu' : 'Open menu'}
            onClick={() => setMenuOpen((open) => !open)}
          >
            {menuOpen ? (
              <X aria-hidden className="size-5" />
            ) : (
              <Menu aria-hidden className="size-5" />
            )}
          </button>
        </div>
      </nav>

      {menuOpen && (
        <div
          id="mobile-nav"
          className="border-t border-[var(--divider)] bg-[var(--canvas)] px-4 py-3 md:hidden"
        >
          <div className="page-wrap flex flex-col gap-1">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className="flex min-h-11 items-center rounded-lg px-3 text-sm font-medium text-[var(--ink-secondary)] no-underline hover:bg-[var(--panel)] hover:text-[var(--ink)]"
                activeProps={{
                  className:
                    'flex min-h-11 items-center rounded-lg px-3 text-sm font-medium text-[var(--primary)] no-underline bg-[var(--primary-tint)]',
                }}
                onClick={() => setMenuOpen(false)}
              >
                {link.label}
              </Link>
            ))}
            <div className="mt-2 flex min-h-11 items-center border-t border-[var(--divider)] pt-3">
              {profileSelect}
            </div>
          </div>
        </div>
      )}
    </header>
  )
}
