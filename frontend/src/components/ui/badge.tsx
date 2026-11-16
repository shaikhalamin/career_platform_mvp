import * as React from 'react'
import { Slot } from 'radix-ui'
import { cva } from 'class-variance-authority'
import type { VariantProps } from 'class-variance-authority'
import { cn } from 'cn'

const badgeVariants = cva(
  'inline-flex w-fit shrink-0 items-center justify-center gap-1 whitespace-nowrap rounded-full border px-2.5 py-0.5 text-xs font-medium [&>svg]:pointer-events-none [&>svg]:size-3 [&>svg]:shrink-0',
  {
    variants: {
      variant: {
        default: 'border-transparent bg-primary text-primary-foreground',
        secondary: 'border-transparent bg-muted text-ink-secondary',
        outline: 'border-divider text-ink-secondary',
        success:
          'border-transparent bg-[color-mix(in_oklab,var(--status-success)_12%,transparent)] text-[var(--status-success)]',
        warning:
          'border-transparent bg-[color-mix(in_oklab,var(--status-warning)_12%,transparent)] text-[var(--status-warning)]',
        danger:
          'border-transparent bg-[color-mix(in_oklab,var(--status-danger)_10%,transparent)] text-[var(--status-danger)]',
        'success-outline':
          'border-[color-mix(in_oklab,var(--status-success)_35%,transparent)] bg-transparent text-[var(--status-success)]',
        'warning-outline':
          'border-[color-mix(in_oklab,var(--status-warning)_40%,transparent)] bg-transparent text-[var(--status-warning)]',
        'danger-outline':
          'border-[color-mix(in_oklab,var(--status-danger)_35%,transparent)] bg-transparent text-[var(--status-danger)]',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  },
)

function Badge({
  className,
  variant,
  asChild = false,
  ...props
}: React.ComponentProps<'span'> &
  VariantProps<typeof badgeVariants> & { asChild?: boolean }) {
  const Comp = asChild ? Slot.Root : 'span'
  return (
    <Comp
      data-slot="badge"
      className={cn(badgeVariants({ variant }), className)}
      {...props}
    />
  )
}

export { Badge, badgeVariants }
