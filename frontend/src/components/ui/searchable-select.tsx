import { useEffect, useMemo, useRef, useState } from 'react'
import { Popover as PopoverPrimitive } from 'radix-ui'
import { CheckIcon, ChevronDownIcon, SearchIcon } from 'lucide-react'

import { cn } from 'cn'

/**
 * A select with built-in search — for option lists too long to scan
 * (e.g. the full country taxonomy). Filtering matches the label plus any
 * keyword aliases, and the list is fully keyboard-navigable.
 */

export interface SearchableSelectOption {
  label: string
  value: string
  disabled?: boolean
  /** Extra lowercase terms that also match this option (e.g. ISO codes). */
  keywords?: string[]
  /** Muted right-aligned annotation (e.g. the region). */
  hint?: string
}

export function SearchableSelect({
  id,
  value,
  onValueChange,
  options,
  placeholder = 'Select…',
  searchPlaceholder = 'Search…',
  emptyMessage = 'No matches.',
  clearLabel,
  size = 'default',
  className,
  disabled,
}: {
  id?: string
  value: string
  onValueChange: (value: string) => void
  options: SearchableSelectOption[]
  placeholder?: string
  searchPlaceholder?: string
  emptyMessage?: string
  /** When set, a leading item with this label selects '' (clears the value). */
  clearLabel?: string
  size?: 'sm' | 'default'
  className?: string
  disabled?: boolean
}) {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const [activeIndex, setActiveIndex] = useState(0)
  const listRef = useRef<HTMLDivElement>(null)

  const normalizedQuery = query.trim().toLowerCase()
  const filtered = useMemo(
    () =>
      normalizedQuery
        ? options.filter(
            (option) =>
              option.label.toLowerCase().includes(normalizedQuery) ||
              option.keywords?.some((keyword) =>
                keyword.includes(normalizedQuery),
              ),
          )
        : options,
    [options, normalizedQuery],
  )

  // Fresh search + highlight whenever the popover opens.
  useEffect(() => {
    if (open) {
      setQuery('')
      setActiveIndex(
        Math.max(
          0,
          filtered.findIndex((option) => option.value === value),
        ),
      )
    }
    // Runs on open only: fresh search + highlight every time.
  }, [open])

  // Keep the highlighted item visible while arrowing through the list.
  useEffect(() => {
    listRef.current
      ?.querySelector(`[data-index="${activeIndex}"]`)
      ?.scrollIntoView({ block: 'nearest' })
  }, [activeIndex])

  const select = (option: SearchableSelectOption) => {
    if (option.disabled) return
    onValueChange(option.value)
    setOpen(false)
  }

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      event.preventDefault()
      setActiveIndex((index) => {
        const last = filtered.length - 1
        if (event.key === 'ArrowDown') return index >= last ? 0 : index + 1
        return index <= 0 ? last : index - 1
      })
    } else if (event.key === 'Home' || event.key === 'End') {
      event.preventDefault()
      setActiveIndex(event.key === 'Home' ? 0 : filtered.length - 1)
    } else if (event.key === 'Enter') {
      event.preventDefault()
      select(filtered[activeIndex])
    }
  }

  const selected = options.find((option) => option.value === value)

  return (
    <PopoverPrimitive.Root open={open} onOpenChange={setOpen}>
      <PopoverPrimitive.Trigger
        id={id}
        type="button"
        disabled={disabled}
        aria-haspopup="listbox"
        aria-expanded={open}
        data-size={size}
        className={cn(
          'flex w-full items-center justify-between gap-2 rounded-md border border-input bg-transparent px-3 text-sm whitespace-nowrap shadow-xs transition-[color,box-shadow] outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 disabled:cursor-not-allowed disabled:opacity-50 data-[placeholder]:text-muted-foreground data-[size=default]:h-9 data-[size=sm]:h-8',
          !selected && 'text-muted-foreground',
          className,
        )}
      >
        {selected ? selected.label : placeholder}
        <ChevronDownIcon className="size-4 shrink-0 opacity-50" />
      </PopoverPrimitive.Trigger>
      <PopoverPrimitive.Portal>
        <PopoverPrimitive.Content
          align="start"
          sideOffset={4}
          className="z-50 w-[var(--radix-popover-trigger-width)] min-w-56 overflow-hidden rounded-md border bg-popover text-popover-foreground shadow-md data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:animate-in data-[state=open]:fade-in-0"
        >
          <div className="flex items-center gap-2 border-b px-2.5">
            <SearchIcon
              aria-hidden
              className="size-4 shrink-0 text-muted-foreground"
            />
            <input
              autoFocus
              value={query}
              onChange={(e) => {
                setQuery(e.target.value)
                setActiveIndex(0)
              }}
              onKeyDown={handleKeyDown}
              placeholder={searchPlaceholder}
              aria-label={searchPlaceholder}
              className="h-9 w-full bg-transparent text-sm outline-none placeholder:text-muted-foreground"
            />
          </div>
          <div
            ref={listRef}
            role="listbox"
            aria-label={placeholder}
            className="max-h-64 overflow-y-auto p-1"
          >
            {clearLabel && !normalizedQuery && (
              <button
                type="button"
                role="option"
                aria-selected={value === ''}
                onClick={() => {
                  onValueChange('')
                  setOpen(false)
                }}
                className="flex w-full cursor-default items-center gap-2 rounded-sm px-2 py-1.5 text-sm font-medium outline-hidden select-none hover:bg-accent hover:text-accent-foreground"
              >
                {clearLabel}
              </button>
            )}
            {filtered.length === 0 ? (
              <p className="px-2 py-4 text-center text-sm text-muted-foreground">
                {emptyMessage}
              </p>
            ) : (
              filtered.map((option, index) => (
                <button
                  key={option.value}
                  type="button"
                  role="option"
                  aria-selected={option.value === value}
                  aria-disabled={option.disabled}
                  data-index={index}
                  onClick={() => select(option)}
                  onMouseEnter={() => setActiveIndex(index)}
                  className={cn(
                    'relative flex w-full cursor-default items-center gap-2 rounded-sm py-1.5 pr-8 pl-2 text-sm outline-hidden select-none',
                    option.disabled
                      ? 'pointer-events-none opacity-50'
                      : 'hover:bg-accent hover:text-accent-foreground',
                    index === activeIndex && 'bg-accent text-accent-foreground',
                  )}
                >
                  <span className="flex-1 truncate text-left">
                    {option.label}
                  </span>
                  {option.hint && (
                    <span className="shrink-0 text-xs font-normal text-muted-foreground">
                      {option.hint}
                    </span>
                  )}
                  {option.value === value && (
                    <CheckIcon
                      aria-hidden
                      className="absolute right-2 size-4 shrink-0"
                    />
                  )}
                </button>
              ))
            )}
          </div>
        </PopoverPrimitive.Content>
      </PopoverPrimitive.Portal>
    </PopoverPrimitive.Root>
  )
}
