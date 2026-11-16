import { useState } from 'react'

import { useAppForm } from '#/hooks/career.form'
import { toFormErrors } from '#/lib/api-errors'
import {
  careerFormSchema,
  emptyFormValues,
  formValuesToApiPayload,
  taxonomyToOptions,
} from '#/lib/career-form'
import type { CareerFormValues, TaxonomyOptions } from '#/lib/career-form'
import { useGetTaxonomyApiV1MetaTaxonomyGet } from '#/gen/queries/meta/useGetTaxonomyApiV1MetaTaxonomyGet'

/**
 * The hybrid career-profile form (create + edit share it): dropdowns for
 * degree/language proficiencies/work authorisation, free-text chips for
 * skills, interests, areas and preferred countries. Validated with zod
 * locally; the backend re-validates and canonicalizes.
 */

const EMPTY_OPTIONS: TaxonomyOptions = {
  degreeLevels: [],
  languageLevels: [],
  languages: [],
  countries: [],
  skills: [],
  tracks: [],
}

export function CareerProfileForm({
  initialValues,
  submitLabel,
  onSubmit,
  eyebrow,
  title,
  subtitle,
}: {
  initialValues?: CareerFormValues
  submitLabel: string
  onSubmit: (
    payload: ReturnType<typeof formValuesToApiPayload>,
  ) => Promise<void>
  eyebrow: string
  title: string
  subtitle: string
}) {
  const [submitError, setSubmitError] = useState<string | null>(null)
  const taxonomyQuery = useGetTaxonomyApiV1MetaTaxonomyGet()
  const options = taxonomyQuery.data?.data
    ? taxonomyToOptions(taxonomyQuery.data.data)
    : EMPTY_OPTIONS

  const form = useAppForm({
    defaultValues: initialValues ?? emptyFormValues(),
    validators: {
      // onChange (not onBlur): errors appear AND clear as values change —
      // chips added later immediately clear "add at least one" messages.
      onChange: careerFormSchema,
    },
    onSubmit: async ({ value }) => {
      setSubmitError(null)
      const parsed = careerFormSchema.safeParse(value)
      if (!parsed.success) {
        setSubmitError('Please fix the highlighted fields before saving.')
        return
      }
      try {
        await onSubmit(formValuesToApiPayload(parsed.data))
      } catch (error) {
        const { form: formMessage, fields } = toFormErrors(error)
        setSubmitError(formMessage ?? 'Saving failed.')
        if (Object.keys(fields).length > 0) {
          form.setErrorMap({
            onSubmit: { form: formMessage ?? undefined, fields },
          })
        }
      }
    },
  })

  if (taxonomyQuery.isError) {
    return (
      <p className="text-sm font-semibold text-red-600">
        Failed to load the skills/country taxonomy — is the backend running on
        port 8000?
      </p>
    )
  }

  return (
    <section className="panel-card mx-auto w-full max-w-3xl p-6 sm:p-8">
      <div className="mb-6">
        <p className="tier-eyebrow mb-2">{eyebrow}</p>
        <h1 className="display-title m-0 text-2xl font-semibold tracking-tight text-[var(--ink)]">
          {title}
        </h1>
        <p className="mt-2 text-sm text-[var(--ink-secondary)]">{subtitle}</p>
      </div>

      {submitError && (
        <div
          role="alert"
          className="mb-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-semibold text-red-700"
        >
          {submitError}
        </div>
      )}

      <form
        onSubmit={(e) => {
          e.preventDefault()
          e.stopPropagation()
          form.handleSubmit()
        }}
        className="space-y-7"
      >
        <fieldset className="space-y-5" disabled={taxonomyQuery.isPending}>
          <legend className="mb-1 text-xs font-bold uppercase tracking-wider text-[var(--ink-secondary)]">
            About you
          </legend>
          <div className="grid gap-5 sm:grid-cols-2">
            <form.AppField name="name">
              {(field) => (
                <field.TextField label="Full name" placeholder="Nusrat Jahan" />
              )}
            </form.AppField>
            <form.AppField name="email">
              {(field) => (
                <field.TextField
                  label="Email"
                  placeholder="nusrat@example.com"
                  hint="Used as your profile handle — no signup or password."
                />
              )}
            </form.AppField>
          </div>
          <form.AppField name="currently_enrolled">
            {(field) => (
              <field.TriStateSwitchField
                label="Currently enrolled in study"
                hint="Some internships require active enrollment. Leave unset if you'd rather verify later."
              />
            )}
          </form.AppField>
          <form.AppField name="citizenship">
            {(field) => (
              <field.TextField
                label="Citizenship (optional)"
                placeholder="e.g. Bangladesh"
                hint="Used only for citizenship-restricted roles. Blank means 'not stated' — never assumed."
              />
            )}
          </form.AppField>
        </fieldset>

        <fieldset className="space-y-5" disabled={taxonomyQuery.isPending}>
          <legend className="mb-1 text-xs font-bold uppercase tracking-wider text-[var(--ink-secondary)]">
            Education &amp; experience
          </legend>
          <div className="grid gap-5 sm:grid-cols-2">
            <form.AppField name="education_level">
              {(field) => (
                <field.SelectField
                  label="Highest education"
                  values={options.degreeLevels}
                />
              )}
            </form.AppField>
            <form.AppField name="education_field">
              {(field) => (
                <field.TextField
                  label="Field of study"
                  placeholder="Business Administration"
                  hint="Matched loosely against each role's relevant fields."
                />
              )}
            </form.AppField>
          </div>
          <form.AppField name="experience_years">
            {(field) => (
              <field.SliderField
                label="Years of work experience"
                max={30}
                format={(v) => `${v} yr${v === 1 ? '' : 's'}`}
              />
            )}
          </form.AppField>
          <form.AppField name="experience_areas">
            {(field) => (
              <field.ChipsField
                label="Experience areas"
                placeholder="e.g. business operations"
                hint="Where you've actually worked, not just skills."
                suggestions={options.tracks}
              />
            )}
          </form.AppField>
        </fieldset>

        <fieldset className="space-y-5" disabled={taxonomyQuery.isPending}>
          <legend className="mb-1 text-xs font-bold uppercase tracking-wider text-[var(--ink-secondary)]">
            Skills &amp; interests
          </legend>
          <form.AppField name="skills">
            {(field) => (
              <field.ChipsField
                label="Skills"
                placeholder="Type a skill and press Enter"
                hint="Free text — the backend maps aliases (e.g. 'MS Excel' → 'Excel')."
                suggestions={options.skills}
              />
            )}
          </form.AppField>
          <form.AppField name="career_interests">
            {(field) => (
              <field.ChipsField
                label="Career interests"
                placeholder="e.g. programme support"
                suggestions={options.tracks}
              />
            )}
          </form.AppField>
        </fieldset>

        <fieldset className="space-y-5" disabled={taxonomyQuery.isPending}>
          <legend className="mb-1 text-xs font-bold uppercase tracking-wider text-[var(--ink-secondary)]">
            Languages &amp; locations
          </legend>
          <form.AppField name="languages">
            {(field) => (
              <field.LanguageRowsField
                label="Languages you speak"
                languages={options.languages}
                levels={options.languageLevels}
              />
            )}
          </form.AppField>
          <form.AppField name="preferred_locations">
            {(field) => (
              <field.ChipsField
                label="Preferred countries"
                placeholder="e.g. Germany"
                hint="Roles in the same region as a preference also earn partial location credit."
                suggestions={options.countries}
              />
            )}
          </form.AppField>
          <form.AppField name="work_authorisation">
            {(field) => (
              <field.WorkAuthRowsField
                label="Work authorisation by country (optional)"
                countries={options.countries}
                hint="'Unknown' is a valid answer — the platform will flag those roles as requiring verification instead of assuming anything."
              />
            )}
          </form.AppField>
        </fieldset>

        <div className="flex justify-end border-t border-[var(--divider)] pt-5">
          <form.AppForm>
            <form.SubscribeButton label={submitLabel} />
          </form.AppForm>
        </div>
      </form>
    </section>
  )
}
