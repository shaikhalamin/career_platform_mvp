import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { useQueryClient } from '@tanstack/react-query'

import { CareerProfileForm } from '#/components/career-profile-form'
import { useActiveProfile } from '#/lib/active-profile'
import { listProfilesApiV1ProfilesGetQueryKey } from '#/gen/queries/profiles/useListProfilesApiV1ProfilesGet'
import { useCreateProfileApiV1ProfilesPost } from '#/gen/queries/profiles/useCreateProfileApiV1ProfilesPost'

export const Route = createFileRoute('/profiles/new')({
  component: NewProfilePage,
})

function NewProfilePage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { setActiveProfile } = useActiveProfile()

  const createProfile = useCreateProfileApiV1ProfilesPost()

  return (
    <main className="page-wrap py-10">
      <CareerProfileForm
        eyebrow="Create your career profile"
        title="Tell us where you're starting from"
        subtitle="Everything here feeds the matching engine: skills overlap, experience alignment, education relevance, location and language fit, plus eligibility checks."
        submitLabel={
          createProfile.isPending ? 'Creating…' : 'Create profile & get matches'
        }
        onSubmit={async (payload) => {
          const result = await createProfile.mutateAsync({ body: payload })
          if (!result.data)
            throw new Error('Profile creation returned no data.')
          setActiveProfile(result.data.id)
          await queryClient.invalidateQueries({
            queryKey: listProfilesApiV1ProfilesGetQueryKey(),
          })
          await navigate({ to: '/recommendations' })
        }}
      />
    </main>
  )
}
