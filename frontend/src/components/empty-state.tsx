import type { ComponentType, ReactNode } from 'react'

/**
 * Friendly empty/loading-fallback state: icon tile, title, description and
 * optional actions. Used for empty lists and "pick a profile first" views.
 */
export function EmptyState({
  icon: Icon,
  title,
  description,
  actions,
}: {
  icon: ComponentType<{ className?: string; 'aria-hidden'?: boolean }>
  title: string
  description: ReactNode
  actions?: ReactNode
}) {
  return (
    <div className="panel-card mx-auto flex w-full max-w-lg flex-col items-center px-8 py-14 text-center">
      <span
        aria-hidden
        className="mb-4 inline-flex size-12 items-center justify-center rounded-full bg-[var(--primary-tint)] text-[var(--primary)]"
      >
        <Icon className="size-6" />
      </span>
      <h2 className="m-0 text-xl font-semibold tracking-tight text-[var(--ink)]">
        {title}
      </h2>
      <p className="mt-2 max-w-sm text-sm leading-relaxed text-[var(--ink-secondary)]">
        {description}
      </p>
      {actions && (
        <div className="mt-6 flex flex-wrap justify-center gap-3">
          {actions}
        </div>
      )}
    </div>
  )
}
