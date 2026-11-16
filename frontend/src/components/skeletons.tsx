import { Skeleton } from '#/components/ui/skeleton'

/**
 * Layout-stable loading placeholders so pages don't jump while queries
 * resolve. Shapes mirror the real card layouts they stand in for.
 */

export function PageHeaderSkeleton() {
  return (
    <div className="mb-8 space-y-3">
      <Skeleton className="h-3 w-32 rounded-full" />
      <Skeleton className="h-9 w-72" />
      <Skeleton className="h-4 w-96 max-w-full" />
    </div>
  )
}

export function CardGridSkeleton({
  count = 6,
  className = 'sm:grid-cols-2 lg:grid-cols-3',
}: {
  count?: number
  className?: string
}) {
  return (
    <div className={`grid gap-4 ${className}`} aria-busy="true">
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="panel-card space-y-3 p-5">
          <div className="flex items-start gap-3">
            <Skeleton className="size-10 rounded-lg" />
            <div className="flex-1 space-y-2">
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-3 w-1/2" />
            </div>
          </div>
          <Skeleton className="h-3 w-full" />
          <Skeleton className="h-3 w-5/6" />
          <div className="flex gap-2 pt-2">
            <Skeleton className="h-5 w-16 rounded-full" />
            <Skeleton className="h-5 w-20 rounded-full" />
            <Skeleton className="h-5 w-14 rounded-full" />
          </div>
        </div>
      ))}
    </div>
  )
}

export function ListRowsSkeleton({ count = 4 }: { count?: number }) {
  return (
    <div className="space-y-4" aria-busy="true">
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="panel-card space-y-3 p-5">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 space-y-2">
              <Skeleton className="h-4 w-2/3" />
              <Skeleton className="h-3 w-1/2" />
            </div>
            <Skeleton className="size-14 rounded-full" />
          </div>
          <Skeleton className="h-3 w-full" />
          <Skeleton className="h-3 w-4/5" />
        </div>
      ))}
    </div>
  )
}

export function DetailPageSkeleton() {
  return (
    <div className="space-y-6" aria-busy="true">
      <Skeleton className="h-4 w-32" />
      <div className="space-y-3">
        <Skeleton className="h-8 w-2/3" />
        <Skeleton className="h-4 w-1/2" />
        <Skeleton className="h-4 w-full max-w-xl" />
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="panel-card space-y-3 p-6">
          {Array.from({ length: 6 }).map((_, index) => (
            <Skeleton key={index} className="h-4 w-full" />
          ))}
        </div>
        <div className="panel-card space-y-3 p-6">
          <Skeleton className="mx-auto size-32 rounded-full" />
          {Array.from({ length: 4 }).map((_, index) => (
            <Skeleton key={index} className="h-3 w-full" />
          ))}
        </div>
      </div>
    </div>
  )
}

export function FormSkeleton() {
  return (
    <div
      className="panel-card mx-auto w-full max-w-3xl p-6 sm:p-8"
      aria-busy="true"
    >
      <div className="mb-8 space-y-3">
        <Skeleton className="h-3 w-36 rounded-full" />
        <Skeleton className="h-7 w-64" />
        <Skeleton className="h-4 w-full max-w-lg" />
      </div>
      <div className="space-y-10">
        {Array.from({ length: 4 }).map((_, section) => (
          <div key={section} className="space-y-5">
            <Skeleton className="h-3 w-28 rounded-full" />
            <div className="grid gap-5 sm:grid-cols-2">
              <div className="space-y-2">
                <Skeleton className="h-3.5 w-20" />
                <Skeleton className="h-9 w-full rounded-md" />
              </div>
              <div className="space-y-2">
                <Skeleton className="h-3.5 w-24" />
                <Skeleton className="h-9 w-full rounded-md" />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
