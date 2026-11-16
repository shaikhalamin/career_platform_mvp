import { useState } from 'react'
import { createFileRoute, Link, useNavigate } from '@tanstack/react-router'
import { useQueryClient } from '@tanstack/react-query'
import {
  Briefcase,
  GraduationCap,
  MapPin,
  Plus,
  Trash2,
  UserRound,
  Wrench,
} from 'lucide-react'

import { Badge } from '#/components/ui/badge'
import { Button } from '#/components/ui/button'
import { PageHeader } from '#/components/page-header'
import { EmptyState } from '#/components/empty-state'
import { CardGridSkeleton } from '#/components/skeletons'
import { ConfirmDialog } from '#/components/confirm-dialog'
import { useActiveProfile } from '#/lib/active-profile'
import {
  listProfilesApiV1ProfilesGetQueryKey,
  useListProfilesApiV1ProfilesGet,
} from '#/gen/queries/profiles/useListProfilesApiV1ProfilesGet'
import { useDeleteProfileApiV1ProfilesProfileIdDelete } from '#/gen/queries/profiles/useDeleteProfileApiV1ProfilesProfileIdDelete'

export const Route = createFileRoute('/profiles/')({
  component: ProfilesPage,
})

/** Deterministic avatar hue per profile name. */
const AVATAR_HUES = [197, 12, 150, 262, 33, 0, 45, 220]

function initials(name: string) {
  return name
    .split(/\s+/)
    .slice(0, 2)
    .map((word) => word.charAt(0).toUpperCase())
    .join('')
}

/**
 * Profile switcher — no signup: anyone can create a profile and switch
 * between them; the active one is remembered in this browser.
 */
function ProfilesPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { activeProfileId, setActiveProfile } = useActiveProfile()
  const [pendingDelete, setPendingDelete] = useState<number | null>(null)
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
      <PageHeader
        eyebrow="No signup — just profiles"
        title="Profiles"
        description="Several people can share this prototype: create a profile each and switch between them. The active profile drives recommendations and the shortlist."
        actions={
          <Button asChild>
            <Link to="/profiles/new">
              <Plus aria-hidden />
              New profile
            </Link>
          </Button>
        }
      />

      {listQuery.isPending ? (
        <CardGridSkeleton count={3} />
      ) : profiles.length === 0 ? (
        <EmptyState
          icon={UserRound}
          title="No profiles yet"
          description="Create the first one to start matching — it takes about three minutes and needs no signup."
          actions={
            <Button asChild>
              <Link to="/profiles/new">
                <Plus aria-hidden />
                Create a profile
              </Link>
            </Button>
          }
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {profiles.map((profile) => {
            const isActive = profile.id === activeProfileId
            const hue =
              AVATAR_HUES[
                profile.name
                  .split('')
                  .reduce((sum, char) => sum + char.charCodeAt(0), 0) %
                  AVATAR_HUES.length
              ]
            return (
              <article
                key={profile.id}
                className={`panel-card flex flex-col p-5 ${
                  isActive
                    ? 'border-[color-mix(in_oklab,var(--primary)_45%,var(--divider))] ring-1 ring-[color-mix(in_oklab,var(--primary)_25%,transparent)]'
                    : ''
                }`}
              >
                <div className="mb-3 flex items-center gap-3">
                  <span
                    aria-hidden
                    className="inline-flex size-10 shrink-0 items-center justify-center rounded-lg text-sm font-semibold"
                    style={{
                      backgroundColor: `oklch(0.93 0.04 ${hue})`,
                      color: `oklch(0.45 0.11 ${hue})`,
                    }}
                  >
                    {initials(profile.name)}
                  </span>
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <h2 className="m-0 truncate text-base font-semibold text-[var(--ink)]">
                        {profile.name}
                      </h2>
                      {isActive && <Badge variant="success">Active</Badge>}
                    </div>
                    <p className="m-0 truncate text-xs text-[var(--ink-tertiary)]">
                      {profile.email}
                    </p>
                  </div>
                </div>
                <ul className="m-0 flex list-none flex-col gap-1.5 p-0 text-xs text-[var(--ink-secondary)]">
                  <li className="flex items-center gap-1.5">
                    <GraduationCap
                      aria-hidden
                      className="size-3.5 text-[var(--ink-tertiary)]"
                    />
                    {profile.education_level}
                  </li>
                  <li className="flex items-center gap-1.5">
                    <Briefcase
                      aria-hidden
                      className="size-3.5 text-[var(--ink-tertiary)]"
                    />
                    {profile.experience_years} yrs experience
                  </li>
                  <li className="flex items-center gap-1.5">
                    <Wrench
                      aria-hidden
                      className="size-3.5 text-[var(--ink-tertiary)]"
                    />
                    {profile.skills.length} skills
                  </li>
                  <li className="flex items-center gap-1.5">
                    <MapPin
                      aria-hidden
                      className="size-3.5 text-[var(--ink-tertiary)]"
                    />
                    <span className="truncate">
                      Prefers {profile.preferred_locations.join(', ') || '—'}
                    </span>
                  </li>
                </ul>
                <div className="mt-4 flex flex-wrap items-center gap-2 border-t border-[var(--divider)] pt-4">
                  {isActive ? (
                    <Button
                      size="sm"
                      onClick={() => navigate({ to: '/recommendations' })}
                    >
                      View recommendations
                    </Button>
                  ) : (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setActiveProfile(profile.id)}
                    >
                      Use this profile
                    </Button>
                  )}
                  <Button asChild variant="ghost" size="sm">
                    <Link
                      to="/profiles/$profileId/edit"
                      params={{ profileId: String(profile.id) }}
                    >
                      Edit
                    </Link>
                  </Button>
                  <ConfirmDialog
                    open={pendingDelete === profile.id}
                    onOpenChange={(open) =>
                      setPendingDelete(open ? profile.id : null)
                    }
                    title={`Delete ${profile.name}?`}
                    description="This permanently removes the profile and its shortlist. This cannot be undone."
                    pending={deleteProfile.isPending}
                    onConfirm={() => {
                      deleteProfile.mutate(
                        { path: { profile_id: profile.id } },
                        { onSettled: () => setPendingDelete(null) },
                      )
                    }}
                  >
                    <Button
                      variant="ghost"
                      size="icon-sm"
                      className="ml-auto text-[var(--error)] hover:bg-[color-mix(in_oklab,var(--error)_10%,transparent)] hover:text-[var(--error)]"
                      disabled={deleteProfile.isPending}
                      aria-label={`Delete ${profile.name}`}
                    >
                      <Trash2 aria-hidden />
                    </Button>
                  </ConfirmDialog>
                </div>
              </article>
            )
          })}
        </div>
      )}
    </main>
  )
}
