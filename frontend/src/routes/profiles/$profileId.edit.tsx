import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { useQueryClient } from '@tanstack/react-query'

import { Button } from '#/components/ui/button'
import { CareerProfileForm } from '#/components/career-profile-form'
import { useActiveProfile } from '#/lib/active-profile'
import { profileToFormValues } from '#/lib/career-form'
import {
  getProfileApiV1ProfilesProfileIdGetQueryKey,
  useGetProfileApiV1ProfilesProfileIdGet,
} from '#/gen/queries/profiles/useGetProfileApiV1ProfilesProfileIdGet'
import { listProfilesApiV1ProfilesGetQueryKey } from '#/gen/queries/profiles/useListProfilesApiV1ProfilesGet'
import { useUpdateProfileApiV1ProfilesProfileIdPatch } from '#/gen/queries/profiles/useUpdateProfileApiV1ProfilesProfileIdPatch'

export const Route = createFileRoute('/profiles/$profileId/edit')({
  component: EditProfilePage,
})

function EditProfilePage() {
  const { profileId } = Route.useParams()
  const profileIdNum = Number(profileId)

  if (!Number.isInteger(profileIdNum) || profileIdNum < 1) {
    return (
      <main className="page-wrap py-10">
        <p className="text-sm font-semibold text-red-600">
          Invalid profile id: {profileId}
        </p>
      </main>
    )
  }

  return <EditProfileForm profileId={profileIdNum} />
}

function EditProfileForm({ profileId }: { profileId: number }) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { setActiveProfile } = useActiveProfile()

  const profileQuery = useGetProfileApiV1ProfilesProfileIdGet({
    path: { profile_id: profileId },
  })

  const updateProfile = useUpdateProfileApiV1ProfilesProfileIdPatch()

  if (profileQuery.isPending) {
    return (
      <main className="page-wrap py-10">
        <p className="text-sm text-[var(--ink-secondary)]">Loading profile…</p>
      </main>
    )
  }

  if (profileQuery.isError || !profileQuery.data.data) {
    return (
      <main className="page-wrap py-10">
        <p className="text-sm font-semibold text-red-600">
          Profile {profileId} not found.
        </p>
        <Button asChild variant="outline" size="xs" className="mt-4">
          <a href="/profiles">Back to profiles</a>
        </Button>
      </main>
    )
  }

  const profile = profileQuery.data.data

  return (
    <main className="page-wrap py-10">
      <CareerProfileForm
        key={profile.id}
        initialValues={profileToFormValues(profile)}
        eyebrow={`Edit profile · ${profile.name}`}
        title="Update your career profile"
        subtitle="Recommendations recalculate automatically the moment you save — scores, eligibility flags and gaps all refresh."
        submitLabel={
          updateProfile.isPending ? 'Saving…' : 'Save & recalculate matches'
        }
        onSubmit={async (payload) => {
          await updateProfile.mutateAsync({
            path: { profile_id: profileId },
            body: payload,
          })
          setActiveProfile(profileId)
          await Promise.all([
            queryClient.invalidateQueries({
              queryKey: getProfileApiV1ProfilesProfileIdGetQueryKey({
                path: { profile_id: profileId },
              }),
            }),
            queryClient.invalidateQueries({
              queryKey: listProfilesApiV1ProfilesGetQueryKey(),
            }),
            // Prefix match: refresh every recommendations query variant.
            queryClient.invalidateQueries({
              queryKey: [{ url: '/api/v1/recommendations' }],
            }),
          ])
          await navigate({ to: '/recommendations' })
        }}
      />
    </main>
  )
}
