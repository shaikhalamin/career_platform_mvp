import { useState } from 'react'
import { useStore } from '@tanstack/react-form'
import { CircleAlert, X } from 'lucide-react'

import { useFieldContext, useFormContext } from '#/hooks/form-contexts'

import { Button } from '#/components/ui/button'
import { Input } from '#/components/ui/input'
import { Label } from '#/components/ui/label'
import { SearchableSelect } from '#/components/ui/searchable-select'
import type { SearchableSelectOption } from '#/components/ui/searchable-select'
import * as ShadcnSelect from '#/components/ui/select'
import { Slider as ShadcnSlider } from '#/components/ui/slider'
import { Switch as ShadcnSwitch } from '#/components/ui/switch'
import { Textarea as ShadcnTextarea } from '#/components/ui/textarea'

/**
 * Field components for the hybrid career-profile form. Structured enums come
 * from the backend taxonomy; skills/interests/areas are free-text chips the
 * backend canonicalizes.
 */

export interface Option {
  label: string
  value: string
}

function FieldErrors() {
  const field = useFieldContext()
  const errors = useStore(field.store, (state) => state.meta.errors)
  return (
    <>
      {field.state.meta.isTouched &&
        errors.map((error) => (
          <div
            key={typeof error === 'string' ? error : error.message}
            className="mt-1.5 flex items-start gap-1.5 text-xs font-medium text-[var(--error)]"
          >
            <CircleAlert aria-hidden className="mt-0.5 size-3.5 shrink-0" />
            {typeof error === 'string' ? error : error.message}
          </div>
        ))}
    </>
  )
}

function FieldHint({ hint }: { hint: string }) {
  return (
    <p className="mt-1.5 text-xs leading-relaxed text-[var(--ink-tertiary)]">
      {hint}
    </p>
  )
}

export function SubscribeButton({
  label,
  disabled = false,
}: {
  label: string
  disabled?: boolean
}) {
  const form = useFormContext()
  return (
    <form.Subscribe selector={(state) => state.isSubmitting}>
      {(isSubmitting) => (
        <Button
          type="submit"
          disabled={isSubmitting || disabled}
          className="w-full sm:w-auto"
        >
          {label}
        </Button>
      )}
    </form.Subscribe>
  )
}

export function TextField({
  label,
  placeholder,
  hint,
}: {
  label: string
  placeholder?: string
  hint?: string
}) {
  const field = useFieldContext<string>()
  return (
    <div>
      <Label
        htmlFor={label}
        className="mb-2 text-sm font-medium text-[var(--ink)]"
      >
        {label}
      </Label>
      <Input
        id={label}
        value={field.state.value}
        placeholder={placeholder}
        onBlur={field.handleBlur}
        onChange={(e) => field.handleChange(e.target.value)}
      />
      {hint && <FieldHint hint={hint} />}
      <FieldErrors />
    </div>
  )
}

export function TextArea({
  label,
  rows = 3,
}: {
  label: string
  rows?: number
}) {
  const field = useFieldContext<string>()
  return (
    <div>
      <Label
        htmlFor={label}
        className="mb-2 text-sm font-medium text-[var(--ink)]"
      >
        {label}
      </Label>
      <ShadcnTextarea
        id={label}
        rows={rows}
        value={field.state.value}
        onBlur={field.handleBlur}
        onChange={(e) => field.handleChange(e.target.value)}
      />
      <FieldErrors />
    </div>
  )
}

export function SelectField({
  label,
  values,
  placeholder = 'Select…',
  hint,
}: {
  label: string
  values: Option[]
  placeholder?: string
  hint?: string
}) {
  const field = useFieldContext<string>()
  return (
    <div>
      <Label className="mb-2 block text-sm font-medium text-[var(--ink)]">
        {label}
      </Label>
      <ShadcnSelect.Select
        name={field.name}
        value={field.state.value}
        onValueChange={(value) => field.handleChange(value)}
      >
        <ShadcnSelect.SelectTrigger className="w-full">
          <ShadcnSelect.SelectValue placeholder={placeholder} />
        </ShadcnSelect.SelectTrigger>
        <ShadcnSelect.SelectContent className="bg-background text-foreground">
          <ShadcnSelect.SelectGroup>
            <ShadcnSelect.SelectLabel>{label}</ShadcnSelect.SelectLabel>
            {values.map((value) => (
              <ShadcnSelect.SelectItem
                key={value.value}
                value={value.value}
                className="text-foreground"
              >
                {value.label}
              </ShadcnSelect.SelectItem>
            ))}
          </ShadcnSelect.SelectGroup>
        </ShadcnSelect.SelectContent>
      </ShadcnSelect.Select>
      {hint && <FieldHint hint={hint} />}
      <FieldErrors />
    </div>
  )
}

export function SearchableSelectField({
  label,
  options,
  placeholder = 'Select…',
  searchPlaceholder = 'Search…',
  clearLabel,
  hint,
}: {
  label: string
  options: SearchableSelectOption[]
  placeholder?: string
  searchPlaceholder?: string
  clearLabel?: string
  hint?: string
}) {
  const field = useFieldContext<string>()
  return (
    <div>
      <Label className="mb-2 block text-sm font-medium text-[var(--ink)]">
        {label}
      </Label>
      <SearchableSelect
        id={label}
        value={field.state.value}
        onValueChange={(value) => field.handleChange(value)}
        options={options}
        placeholder={placeholder}
        searchPlaceholder={searchPlaceholder}
        clearLabel={clearLabel}
        disabled={options.length === 0}
      />
      {hint && <FieldHint hint={hint} />}
      <FieldErrors />
    </div>
  )
}

export function SliderField({
  label,
  max = 100,
  step = 1,
  format = (v: number) => `${v}`,
}: {
  label: string
  max?: number
  step?: number
  format?: (value: number) => string
}) {
  const field = useFieldContext<number>()
  return (
    <div>
      <div className="mb-2.5 flex items-baseline justify-between">
        <Label
          htmlFor={label}
          className="text-sm font-medium text-[var(--ink)]"
        >
          {label}
        </Label>
        <span className="rounded-md bg-[var(--primary-tint)] px-2 py-0.5 text-sm font-semibold tabular-nums text-[var(--primary-strong)]">
          {format(field.state.value)}
        </span>
      </div>
      <ShadcnSlider
        id={label}
        min={0}
        max={max}
        step={step}
        value={[field.state.value]}
        onValueChange={(value) => field.handleChange(value[0])}
      />
      <FieldErrors />
    </div>
  )
}

export function TriStateSwitchField({
  label,
  hint,
}: {
  label: string
  hint?: string
}) {
  // boolean | null: switch with an explicit "not stated" reset button.
  const field = useFieldContext<boolean | null>()
  const value = field.state.value
  return (
    <div className="flex items-start justify-between gap-4">
      <div className="min-w-0">
        <Label
          htmlFor={label}
          className="text-sm font-medium text-[var(--ink)]"
        >
          {label}
        </Label>
        {hint && <FieldHint hint={hint} />}
      </div>
      <div className="flex shrink-0 items-center gap-2 pt-0.5">
        {value !== null && (
          <button
            type="button"
            className="text-xs text-[var(--ink-tertiary)] underline hover:text-[var(--ink)]"
            onClick={() => field.handleChange(null)}
          >
            clear
          </button>
        )}
        <ShadcnSwitch
          id={label}
          checked={value === true}
          onCheckedChange={(checked) => field.handleChange(checked)}
        />
      </div>
      <FieldErrors />
    </div>
  )
}

export function ChipsField({
  label,
  placeholder,
  hint,
  suggestions = [],
}: {
  label: string
  placeholder?: string
  hint?: string
  suggestions?: string[]
}) {
  const field = useFieldContext<string[]>()
  const [draft, setDraft] = useState('')

  const addChip = () => {
    const chip = draft.trim()
    if (!chip) return
    if (
      !field.state.value.some(
        (existing) => existing.toLowerCase() === chip.toLowerCase(),
      )
    ) {
      field.handleChange([...field.state.value, chip])
    }
    setDraft('')
  }

  const removeChip = (chip: string) => {
    field.handleChange(
      field.state.value.filter((existing) => existing !== chip),
    )
  }

  const unusedSuggestions = suggestions
    .filter(
      (suggestion) =>
        !field.state.value.some(
          (existing) => existing.toLowerCase() === suggestion.toLowerCase(),
        ),
    )
    .slice(0, 8)

  return (
    <div>
      <Label
        htmlFor={label}
        className="mb-2 block text-sm font-medium text-[var(--ink)]"
      >
        {label}
      </Label>
      <div className="flex gap-2">
        <Input
          id={label}
          value={draft}
          placeholder={placeholder}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ',') {
              e.preventDefault()
              addChip()
            }
          }}
          onBlur={() => addChip()}
        />
        <Button type="button" variant="outline" onClick={addChip}>
          Add
        </Button>
      </div>
      {hint && <FieldHint hint={hint} />}
      {field.state.value.length > 0 && (
        <div className="mt-2.5 flex flex-wrap gap-1.5">
          {field.state.value.map((chip) => (
            <span
              key={chip}
              className="inline-flex items-center gap-1 rounded-full border border-[var(--divider)] bg-[var(--primary-tint)] py-1 pr-1 pl-2.5 text-xs font-medium text-[var(--primary-strong)]"
            >
              {chip}
              <button
                type="button"
                aria-label={`Remove ${chip}`}
                className="-mr-0.5 inline-flex size-5 items-center justify-center rounded-full text-[var(--primary-strong)] transition hover:bg-[color-mix(in_oklab,var(--status-danger)_12%,transparent)] hover:text-[var(--status-danger)]"
                onClick={() => removeChip(chip)}
              >
                <X aria-hidden className="size-3" />
              </button>
            </span>
          ))}
        </div>
      )}
      {unusedSuggestions.length > 0 && (
        <div className="mt-2.5 flex flex-wrap items-center gap-1.5">
          <span className="text-xs text-[var(--ink-tertiary)]">
            Suggestions:
          </span>
          {unusedSuggestions.map((suggestion) => (
            <button
              key={suggestion}
              type="button"
              className="rounded-full border border-dashed border-[var(--dashed-border)] px-2.5 py-0.5 text-xs text-[var(--ink-secondary)] transition hover:border-[var(--primary)] hover:bg-[var(--primary-tint)] hover:text-[var(--primary-strong)]"
              onClick={() =>
                field.handleChange([...field.state.value, suggestion])
              }
            >
              + {suggestion}
            </button>
          ))}
        </div>
      )}
      <FieldErrors />
    </div>
  )
}

/**
 * Preferred countries: the full taxonomy list is too long to scan, so
 * countries are added through a searchable picker and shown as removable
 * chips. Only taxonomy entries can be added — no free text, no 422s.
 */
export function CountryChipsField({
  label,
  options,
  searchPlaceholder = 'Search countries by name or code…',
  hint,
}: {
  label: string
  options: SearchableSelectOption[]
  searchPlaceholder?: string
  hint?: string
}) {
  const field = useFieldContext<string[]>()
  const [draft, setDraft] = useState('')
  const selected = new Set(field.state.value)

  const addCountry = (country: string) => {
    if (country && !selected.has(country)) {
      field.handleChange([...field.state.value, country])
    }
    setDraft('')
  }

  return (
    <div>
      <Label className="mb-2 block text-sm font-medium text-[var(--ink)]">
        {label}
      </Label>
      <SearchableSelect
        value={draft}
        onValueChange={addCountry}
        options={options.map((option) => ({
          ...option,
          disabled: selected.has(option.value),
        }))}
        placeholder="Search countries…"
        searchPlaceholder={searchPlaceholder}
        emptyMessage="No country matches that search."
        disabled={options.length === 0}
      />
      {hint && <FieldHint hint={hint} />}
      {field.state.value.length > 0 && (
        <div className="mt-2.5 flex flex-wrap gap-1.5">
          {field.state.value.map((chip) => (
            <span
              key={chip}
              className="inline-flex items-center gap-1 rounded-full border border-[var(--divider)] bg-[var(--primary-tint)] py-1 pr-1 pl-2.5 text-xs font-medium text-[var(--primary-strong)]"
            >
              {chip}
              <button
                type="button"
                aria-label={`Remove ${chip}`}
                className="-mr-0.5 inline-flex size-5 items-center justify-center rounded-full text-[var(--primary-strong)] transition hover:bg-[color-mix(in_oklab,var(--status-danger)_12%,transparent)] hover:text-[var(--status-danger)]"
                onClick={() =>
                  field.handleChange(
                    field.state.value.filter((existing) => existing !== chip),
                  )
                }
              >
                <X aria-hidden className="size-3" />
              </button>
            </span>
          ))}
        </div>
      )}
      <FieldErrors />
    </div>
  )
}

export interface LanguageRow {
  name: string
  level: string
}

export function LanguageRowsField({
  label,
  languages,
  levels,
}: {
  label: string
  languages: string[]
  levels: Option[]
}) {
  const field = useFieldContext<LanguageRow[]>()
  const rows = field.state.value

  const update = (index: number, patch: Partial<LanguageRow>) => {
    field.handleChange(
      rows.map((row, i) => (i === index ? { ...row, ...patch } : row)),
    )
  }

  return (
    <div>
      <Label className="mb-2 block text-sm font-medium text-[var(--ink)]">
        {label}
      </Label>
      <div className="space-y-2">
        {rows.map((row, index) => (
          <div key={index} className="flex items-center gap-2">
            <ShadcnSelect.Select
              value={row.name}
              onValueChange={(value) => update(index, { name: value })}
            >
              <ShadcnSelect.SelectTrigger size="sm" className="w-full min-w-28">
                <ShadcnSelect.SelectValue placeholder="Language" />
              </ShadcnSelect.SelectTrigger>
              <ShadcnSelect.SelectContent className="bg-background text-foreground">
                {languages.map((language) => (
                  <ShadcnSelect.SelectItem key={language} value={language}>
                    {language}
                  </ShadcnSelect.SelectItem>
                ))}
              </ShadcnSelect.SelectContent>
            </ShadcnSelect.Select>
            <ShadcnSelect.Select
              value={row.level}
              onValueChange={(value) => update(index, { level: value })}
            >
              <ShadcnSelect.SelectTrigger size="sm" className="w-full min-w-32">
                <ShadcnSelect.SelectValue placeholder="Proficiency" />
              </ShadcnSelect.SelectTrigger>
              <ShadcnSelect.SelectContent className="bg-background text-foreground">
                {levels.map((level) => (
                  <ShadcnSelect.SelectItem
                    key={level.value}
                    value={level.value}
                  >
                    {level.label}
                  </ShadcnSelect.SelectItem>
                ))}
              </ShadcnSelect.SelectContent>
            </ShadcnSelect.Select>
            <button
              type="button"
              aria-label="Remove language"
              className="inline-flex size-8 shrink-0 items-center justify-center rounded-md text-[var(--ink-tertiary)] transition hover:bg-[color-mix(in_oklab,var(--status-danger)_10%,transparent)] hover:text-[var(--status-danger)]"
              onClick={() =>
                field.handleChange(rows.filter((_, i) => i !== index))
              }
            >
              <X aria-hidden className="size-4" />
            </button>
          </div>
        ))}
      </div>
      <Button
        type="button"
        variant="outline"
        size="sm"
        className="mt-2"
        onClick={() =>
          field.handleChange([
            ...rows,
            { name: 'English', level: 'conversational' },
          ])
        }
      >
        + Add language
      </Button>
      <FieldErrors />
    </div>
  )
}

export interface WorkAuthRow {
  country: string
  status: string
}

const WORK_AUTH_OPTIONS: Option[] = [
  { label: 'Authorized', value: 'authorized' },
  { label: 'Not authorized', value: 'not_authorized' },
  { label: 'Unknown — needs verification', value: 'unknown' },
]

export function WorkAuthRowsField({
  label,
  countries,
  hint,
}: {
  label: string
  countries: SearchableSelectOption[]
  hint?: string
}) {
  const field = useFieldContext<WorkAuthRow[]>()
  const rows = field.state.value
  const usedCountries = new Set(rows.map((row) => row.country))

  const update = (index: number, patch: Partial<WorkAuthRow>) => {
    field.handleChange(
      rows.map((row, i) => (i === index ? { ...row, ...patch } : row)),
    )
  }

  return (
    <div>
      <Label className="mb-2 block text-sm font-medium text-[var(--ink)]">
        {label}
      </Label>
      <div className="space-y-2">
        {rows.map((row, index) => (
          <div key={index} className="flex items-center gap-2">
            <SearchableSelect
              value={row.country}
              onValueChange={(value) => update(index, { country: value })}
              options={countries.map((option) => ({
                ...option,
                disabled:
                  usedCountries.has(option.value) &&
                  option.value !== row.country,
              }))}
              placeholder="Country"
              searchPlaceholder="Search countries by name or code…"
              size="sm"
              className="w-full min-w-32"
            />
            <ShadcnSelect.Select
              value={row.status}
              onValueChange={(value) => update(index, { status: value })}
            >
              <ShadcnSelect.SelectTrigger size="sm" className="w-full min-w-40">
                <ShadcnSelect.SelectValue placeholder="Status" />
              </ShadcnSelect.SelectTrigger>
              <ShadcnSelect.SelectContent className="bg-background text-foreground">
                {WORK_AUTH_OPTIONS.map((option) => (
                  <ShadcnSelect.SelectItem
                    key={option.value}
                    value={option.value}
                  >
                    {option.label}
                  </ShadcnSelect.SelectItem>
                ))}
              </ShadcnSelect.SelectContent>
            </ShadcnSelect.Select>
            <button
              type="button"
              aria-label="Remove entry"
              className="inline-flex size-8 shrink-0 items-center justify-center rounded-md text-[var(--ink-tertiary)] transition hover:bg-[color-mix(in_oklab,var(--status-danger)_10%,transparent)] hover:text-[var(--status-danger)]"
              onClick={() =>
                field.handleChange(rows.filter((_, i) => i !== index))
              }
            >
              <X aria-hidden className="size-4" />
            </button>
          </div>
        ))}
      </div>
      <Button
        type="button"
        variant="outline"
        size="sm"
        className="mt-2"
        onClick={() =>
          field.handleChange([
            ...rows,
            {
              country:
                countries.find((c) => !usedCountries.has(c.value))?.value ??
                (countries.length > 0 ? countries[0].value : ''),
              status: 'unknown',
            },
          ])
        }
      >
        + Add country
      </Button>
      {hint && <FieldHint hint={hint} />}
      <FieldErrors />
    </div>
  )
}
