import type { ReactNode } from 'react'
import { cn } from 'cn'

/**
 * Consistent page opener used across routes: eyebrow, title, optional
 * description and a right-aligned actions slot.
 */
export function PageHeader({
  eyebrow,
  title,
  description,
  actions,
  className,
}: {
  eyebrow?: string
  title: ReactNode
  description?: ReactNode
  actions?: ReactNode
  className?: string
}) {
  return (
    <div
      className={cn(
        'mb-8 flex flex-wrap items-end justify-between gap-x-6 gap-y-4',
        className,
      )}
    >
      <div className="min-w-0 max-w-2xl">
        {eyebrow && <p className="tier-eyebrow mb-2">{eyebrow}</p>}
        <h1 className="display-title m-0 text-3xl tracking-tight">{title}</h1>
        {description && (
          <p className="mt-2 text-sm leading-relaxed text-[var(--ink-secondary)]">
            {description}
          </p>
        )}
      </div>
      {actions && (
        <div className="flex flex-wrap items-center gap-3">{actions}</div>
      )}
    </div>
  )
}
