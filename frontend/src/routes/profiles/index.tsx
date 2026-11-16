import { createFileRoute, Link, useNavigate } from '@tanstack/react-router'
import { useQueryClient } from '@tanstack/react-query'

import { Button } from '#/components/ui/button'
import { useActiveProfile } from '#/lib/active-profile'
import {
  listProfilesApiV1ProfilesGetQueryKey,
  useListProfilesApiV1ProfilesGet,
} from '#/gen/queries/profiles/useListProfilesApiV1ProfilesGet'
import { useDeleteProfileApiV1ProfilesProfileIdDelete } from '#/gen/queries/profiles/useDeleteProfileApiV1ProfilesProfileIdDelete'

export const Route = createFileRoute('/profiles/')({
  component: ProfilesPage,
})

/**
 * Profile switcher — no signup: anyone can create a profile and switch
 * between them; the active one is remembered in this browser.
 */
function ProfilesPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { activeProfileId, setActiveProfile } = useActiveProfile()
  const listQuery = useListProfilesApiV1ProfilesGet({
    query: { page: 1, page_size: 100 },
  })
  const deleteProfile = useDeleteProfileApiV1ProfilesProfileIdDelete({
    mutation: {
      onSuccess: async (_data, variables) => {
        if (activeProfileId === variables.path.profile_id) {
          setActiveProfile(null)
        }
        await queryClient.invalidateQueries({
          queryKey: listProfilesApiV1ProfilesGetQueryKey(),
        })
      },
    },
  })

  const profiles = listQuery.data?.data ?? []

  return (
    <main className="page-wrap py-10">
      <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="tier-eyebrow mb-2">No signup — just profiles</p>
          <h1 className="display-title m-0 text-3xl font-semibold tracking-tight text-[var(--ink)]">
            Profiles
          </h1>
          <p className="mt-2 max-w-xl text-sm text-[var(--ink-secondary)]">
            Several people can share this prototype: create a profile each and
            switch between them. The active profile drives recommendations and
            the shortlist.
          </p>
        </div>
        <Button asChild>
          <Link to="/profiles/new">New profile</Link>
        </Button>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {listQuery.isPending ? (
          <p className="text-sm text-[var(--ink-secondary)]">
            Loading profiles…
          </p>
        ) : profiles.length === 0 ? (
          <div className="panel-card p-8 text-center text-sm text-[var(--ink-secondary)] sm:col-span-2 lg:col-span-3">
            No profiles yet — create the first one to start matching.
          </div>
        ) : (
          profiles.map((profile) => {
            const isActive = profile.id === activeProfileId
            return (
              <article
                key={profile.id}
                className={`panel-card flex flex-col p-5 ${isActive ? 'border-[var(--store-blue)]' : ''}`}
              >
                <div className="mb-1 flex items-center gap-2">
                  <h2 className="m-0 text-base font-semibold text-[var(--ink)]">
                    {profile.name}
                  </h2>
                  {isActive && (
                    <span className="rounded-full bg-[color-mix(in_oklab,var(--store-blue)_12%,transparent)] px-2 py-0.5 text-[10px] font-bold text-[var(--store-blue)]">
                      ACTIVE
                    </span>
                  )}
                </div>
                <p className="m-0 text-xs text-[var(--ink-tertiary)]">
                  {profile.email}
                </p>
                <p className="mt-3 text-xs text-[var(--ink-secondary)]">
                  {profile.education_level} · {profile.experience_years} yrs ·{' '}
                  {profile.skills.length} skills
                </p>
                <p className="mt-1 text-xs text-[var(--ink-secondary)]">
                  Prefers {profile.preferred_locations.join(', ') || '—'}
                </p>
                <div className="mt-4 flex flex-wrap gap-2 border-t border-[var(--divider)] pt-3">
                  {isActive ? (
                    <Button
                      size="xs"
                      onClick={() => navigate({ to: '/recommendations' })}
                    >
                      View recommendations
                    </Button>
                  ) : (
                    <Button
                      size="xs"
                      variant="outline"
                      onClick={() => setActiveProfile(profile.id)}
                    >
                      Use this profile
                    </Button>
                  )}
                  <Button asChild variant="ghost" size="xs">
                    <Link
                      to="/profiles/$profileId/edit"
                      params={{ profileId: String(profile.id) }}
                    >
                      Edit
                    </Link>
                  </Button>
                  <Button
                    variant="ghost"
                    size="xs"
                    className="ml-auto text-red-600 hover:text-red-700"
                    disabled={deleteProfile.isPending}
                    onClick={() =>
                      deleteProfile.mutate({ path: { profile_id: profile.id } })
                    }
                  >
                    Delete
                  </Button>
                </div>
              </article>
            )
          })
        )}
      </div>
    </main>
  )
}
