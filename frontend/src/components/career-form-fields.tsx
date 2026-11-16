import { useState } from 'react'
import { useStore } from '@tanstack/react-form'
import { X } from 'lucide-react'

import { useFieldContext, useFormContext } from '#/hooks/form-contexts'

import { Button } from '#/components/ui/button'
import { Input } from '#/components/ui/input'
import { Label } from '#/components/ui/label'
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
            className="mt-1 text-sm font-semibold text-red-600"
          >
            {typeof error === 'string' ? error : error.message}
          </div>
        ))}
    </>
  )
}

export function SubscribeButton({ label }: { label: string }) {
  const form = useFormContext()
  return (
    <form.Subscribe selector={(state) => state.isSubmitting}>
      {(isSubmitting) => (
        <Button type="submit" disabled={isSubmitting}>
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
        className="mb-2 text-sm font-semibold text-[var(--ink)]"
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
      {hint && (
        <p className="mt-1 text-xs text-[var(--ink-tertiary)]">{hint}</p>
      )}
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
        className="mb-2 text-sm font-semibold text-[var(--ink)]"
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
      <Label className="mb-2 block text-sm font-semibold text-[var(--ink)]">
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
      {hint && (
        <p className="mt-1 text-xs text-[var(--ink-tertiary)]">{hint}</p>
      )}
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
      <div className="mb-2 flex items-baseline justify-between">
        <Label
          htmlFor={label}
          className="text-sm font-semibold text-[var(--ink)]"
        >
          {label}
        </Label>
        <span className="text-sm font-semibold tabular-nums text-[var(--primary)]">
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
      <div>
        <Label
          htmlFor={label}
          className="text-sm font-semibold text-[var(--ink)]"
        >
          {label}
        </Label>
        {hint && (
          <p className="mt-1 text-xs text-[var(--ink-tertiary)]">{hint}</p>
        )}
      </div>
      <div className="flex items-center gap-2">
        {value !== null && (
          <button
            type="button"
            className="text-xs text-[var(--ink-tertiary)] underline"
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
        className="mb-2 block text-sm font-semibold text-[var(--ink)]"
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
      {hint && (
        <p className="mt-1 text-xs text-[var(--ink-tertiary)]">{hint}</p>
      )}
      {field.state.value.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1.5">
          {field.state.value.map((chip) => (
            <span
              key={chip}
              className="inline-flex items-center gap-1 rounded-full border border-[var(--card-border)] bg-[var(--fog)] px-2.5 py-1 text-xs text-[var(--ink)]"
            >
              {chip}
              <button
                type="button"
                aria-label={`Remove ${chip}`}
                className="text-[var(--ink-tertiary)] transition hover:text-[var(--error)]"
                onClick={() => removeChip(chip)}
              >
                <X className="size-3" />
              </button>
            </span>
          ))}
        </div>
      )}
      {unusedSuggestions.length > 0 && (
        <div className="mt-2 flex flex-wrap items-center gap-1">
          <span className="text-[11px] text-[var(--ink-tertiary)]">
            Suggestions:
          </span>
          {unusedSuggestions.map((suggestion) => (
            <button
              key={suggestion}
              type="button"
              className="rounded-full border border-dashed border-[var(--dashed-border)] px-2 py-0.5 text-[11px] text-[var(--ink-secondary)] transition hover:border-[var(--store-blue)] hover:text-[var(--store-blue)]"
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
      <Label className="mb-2 block text-sm font-semibold text-[var(--ink)]">
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
              className="rounded p-1.5 text-[var(--ink-tertiary)] transition hover:bg-[var(--fog)] hover:text-[var(--error)]"
              onClick={() =>
                field.handleChange(rows.filter((_, i) => i !== index))
              }
            >
              <X className="size-4" />
            </button>
          </div>
        ))}
      </div>
      <Button
        type="button"
        variant="outline"
        size="xs"
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
  countries: string[]
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
      <Label className="mb-2 block text-sm font-semibold text-[var(--ink)]">
        {label}
      </Label>
      <div className="space-y-2">
        {rows.map((row, index) => (
          <div key={index} className="flex items-center gap-2">
            <ShadcnSelect.Select
              value={row.country}
              onValueChange={(value) => update(index, { country: value })}
            >
              <ShadcnSelect.SelectTrigger size="sm" className="w-full min-w-32">
                <ShadcnSelect.SelectValue placeholder="Country" />
              </ShadcnSelect.SelectTrigger>
              <ShadcnSelect.SelectContent className="bg-background text-foreground">
                {countries.map((country) => (
                  <ShadcnSelect.SelectItem
                    key={country}
                    value={country}
                    disabled={
                      usedCountries.has(country) && country !== row.country
                    }
                  >
                    {country}
                  </ShadcnSelect.SelectItem>
                ))}
              </ShadcnSelect.SelectContent>
            </ShadcnSelect.Select>
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
              className="rounded p-1.5 text-[var(--ink-tertiary)] transition hover:bg-[var(--fog)] hover:text-[var(--error)]"
              onClick={() =>
                field.handleChange(rows.filter((_, i) => i !== index))
              }
            >
              <X className="size-4" />
            </button>
          </div>
        ))}
      </div>
      <Button
        type="button"
        variant="outline"
        size="xs"
        className="mt-2"
        onClick={() =>
          field.handleChange([
            ...rows,
            {
              country:
                countries.find((c) => !usedCountries.has(c)) ?? countries[0],
              status: 'unknown',
            },
          ])
        }
      >
        + Add country
      </Button>
      {hint && (
        <p className="mt-1 text-xs text-[var(--ink-tertiary)]">{hint}</p>
      )}
      <FieldErrors />
    </div>
  )
}
