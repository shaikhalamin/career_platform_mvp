import { useQueryClient } from '@tanstack/react-query'
import { Heart } from 'lucide-react'

import { Button } from '#/components/ui/button'
import { useAddToShortlistApiV1ShortlistPost } from '#/gen/queries/shortlist/useAddToShortlistApiV1ShortlistPost'
import { useRemoveFromShortlistApiV1ShortlistProfileIdOpportunityIdDelete } from '#/gen/queries/shortlist/useRemoveFromShortlistApiV1ShortlistProfileIdOpportunityIdDelete'

/**
 * Shortlist (wishlist) toggle. Requires an active profile — renders a hint
 * instead when nobody has picked one yet.
 */
export function ShortlistButton({
  profileId,
  opportunityId,
  shortlisted,
  size = 'xs',
}: {
  profileId: number | null
  opportunityId: string
  shortlisted: boolean
  size?: 'xs' | 'sm'
}) {
  const queryClient = useQueryClient()
  const addMutation = useAddToShortlistApiV1ShortlistPost()
  const removeMutation =
    useRemoveFromShortlistApiV1ShortlistProfileIdOpportunityIdDelete()

  if (profileId === null) {
    return (
      <span className="inline-flex items-center gap-1.5 text-xs text-[var(--ink-tertiary)]">
        <Heart aria-hidden className="size-3.5" />
        Pick a profile to shortlist
      </span>
    )
  }

  const pending = addMutation.isPending || removeMutation.isPending

  return (
    <Button
      type="button"
      size={size}
      variant={shortlisted ? 'default' : 'outline'}
      disabled={pending}
      aria-pressed={shortlisted}
      onClick={async () => {
        if (shortlisted) {
          await removeMutation.mutateAsync({
            path: { profile_id: profileId, opportunity_id: opportunityId },
          })
        } else {
          await addMutation.mutateAsync({
            body: { profile_id: profileId, opportunity_id: opportunityId },
          })
        }
        // Refresh everything that shows shortlist state or scores.
        await queryClient.invalidateQueries()
      }}
    >
      <Heart
        className={`size-3.5 ${shortlisted ? 'fill-current' : ''}`}
        aria-hidden
      />
      {shortlisted ? 'Shortlisted' : 'Shortlist'}
    </Button>
  )
}
