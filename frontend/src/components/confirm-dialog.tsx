import * as React from 'react'
import { Dialog as DialogPrimitive } from 'radix-ui'
import { TriangleAlert } from 'lucide-react'

import { Button } from '#/components/ui/button'

/**
 * Small destructive-action confirmation modal. Keeps the trigger fully
 * controlled by the caller; used for things like deleting a profile.
 */
export function ConfirmDialog({
  open,
  onOpenChange,
  title,
  description,
  confirmLabel = 'Delete',
  cancelLabel = 'Cancel',
  pending = false,
  onConfirm,
  children,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  title: string
  description: string
  confirmLabel?: string
  cancelLabel?: string
  pending?: boolean
  onConfirm: () => void
  children: React.ReactNode
}) {
  return (
    <DialogPrimitive.Root open={open} onOpenChange={onOpenChange}>
      <DialogPrimitive.Trigger asChild>{children}</DialogPrimitive.Trigger>
      <DialogPrimitive.Portal>
        <DialogPrimitive.Overlay className="fixed inset-0 z-50 bg-black/50 backdrop-blur-[2px] data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />
        <DialogPrimitive.Content className="fixed top-1/2 left-1/2 z-50 w-[calc(100%-2rem)] max-w-md -translate-x-1/2 -translate-y-1/2 rounded-xl border bg-card p-6 shadow-lg data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95">
          <div className="flex gap-4">
            <span
              aria-hidden
              className="inline-flex size-10 shrink-0 items-center justify-center rounded-full bg-[color-mix(in_oklab,var(--status-danger)_12%,transparent)] text-[var(--status-danger)]"
            >
              <TriangleAlert className="size-5" />
            </span>
            <div className="min-w-0">
              <DialogPrimitive.Title className="m-0 text-lg font-semibold tracking-tight text-[var(--ink)]">
                {title}
              </DialogPrimitive.Title>
              <DialogPrimitive.Description className="mt-1.5 text-sm leading-relaxed text-[var(--ink-secondary)]">
                {description}
              </DialogPrimitive.Description>
            </div>
          </div>
          <div className="mt-6 flex justify-end gap-3">
            <DialogPrimitive.Close asChild>
              <Button variant="outline" disabled={pending}>
                {cancelLabel}
              </Button>
            </DialogPrimitive.Close>
            <Button
              variant="destructive"
              disabled={pending}
              onClick={(e) => {
                e.preventDefault()
                onConfirm()
              }}
            >
              {pending ? 'Deleting…' : confirmLabel}
            </Button>
          </div>
        </DialogPrimitive.Content>
      </DialogPrimitive.Portal>
    </DialogPrimitive.Root>
  )
}
