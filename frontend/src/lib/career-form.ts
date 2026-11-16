import { z } from 'zod'

import type { TaxonomyRead } from '#/gen/types/TaxonomyRead'
import type { ProfileCreate } from '#/gen/types/ProfileCreate'
import type { ProfileRead } from '#/gen/types/ProfileRead'

/**
 * The hybrid career-profile form: structured dropdowns backed by the
 * taxonomy endpoint, free-text chips for skills/interests/areas, repeatable
 * language + work-authorisation rows. Validation mirrors the backend's
 * Pydantic contract (Kubb-generated types keep the payload in sync).
 */

export interface CareerFormValues {
  name: string
  email: string
  education_level: string
  education_field: string
  experience_years: number
  experience_areas: string[]
  skills: string[]
  languages: { name: string; level: string }[]
  preferred_locations: string[]
  career_interests: string[]
  work_authorisation: { country: string; status: string }[]
  citizenship: string
  currently_enrolled: boolean | null
}

export const careerFormSchema = z
  .object({
    name: z.string().trim().min(1, 'Name must not be blank.').max(100),
    email: z.email('Enter a valid email address.').max(320),
    education_level: z.enum([
      'none',
      'secondary',
      'diploma',
      'associate',
      'bachelors',
      'masters',
      'doctorate',
    ]),
    education_field: z.string().max(120),
    experience_years: z.number().min(0).max(50),
    experience_areas: z.array(z.string()).max(10),
    skills: z.array(z.string().trim().min(1)).min(1, 'Add at least one skill.'),
    languages: z
      .array(
        z.object({
          name: z.string().min(1, 'Pick a language.'),
          level: z.string().min(1, 'Pick a proficiency.'),
        }),
      )
      .min(1, 'Add at least one language.'),
    preferred_locations: z
      .array(z.string().trim().min(1))
      .min(1, 'Add at least one preferred country.'),
    career_interests: z.array(z.string().trim().min(1)).max(15),
    work_authorisation: z.array(
      z.object({
        country: z.string().min(1, 'Pick a country.'),
        status: z.enum(['authorized', 'not_authorized', 'unknown']),
      }),
    ),
    citizenship: z.string().max(80),
    currently_enrolled: z.boolean().nullable(),
  })
  .superRefine((values, ctx) => {
    const duplicateCountry = values.work_authorisation.find(
      (row, index) =>
        values.work_authorisation.findIndex(
          (other) => other.country === row.country,
        ) !== index,
    )
    if (duplicateCountry) {
      ctx.addIssue({
        code: 'custom',
        path: ['work_authorisation'],
        message: `Duplicate country: ${duplicateCountry.country}.`,
      })
    }
  })

export function emptyFormValues(): CareerFormValues {
  return {
    name: '',
    email: '',
    education_level: 'bachelors',
    education_field: '',
    experience_years: 0,
    experience_areas: [],
    skills: [],
    languages: [{ name: 'English', level: 'conversational' }],
    preferred_locations: [],
    career_interests: [],
    work_authorisation: [],
    citizenship: '',
    currently_enrolled: null,
  }
}

export function profileToFormValues(profile: ProfileRead): CareerFormValues {
  return {
    name: profile.name,
    email: profile.email,
    education_level: profile.education_level,
    education_field: profile.education_field ?? '',
    experience_years: profile.experience_years,
    experience_areas: profile.experience_areas,
    skills: profile.skills,
    languages: Object.entries(profile.languages).map(([name, level]) => ({
      name,
      level,
    })),
    preferred_locations: profile.preferred_locations,
    career_interests: profile.career_interests,
    work_authorisation: Object.entries(profile.work_authorisation).map(
      ([country, status]) => ({ country, status }),
    ),
    citizenship: profile.citizenship ?? '',
    currently_enrolled: profile.currently_enrolled,
  }
}

export function formValuesToApiPayload(
  values: CareerFormValues,
): ProfileCreate {
  const languages: Record<string, string> = {}
  for (const row of values.languages) {
    if (row.name.trim() && row.level) languages[row.name.trim()] = row.level
  }
  const workAuthorisation: Record<string, string> = {}
  for (const row of values.work_authorisation) {
    if (row.country && row.status) workAuthorisation[row.country] = row.status
  }
  return {
    name: values.name.trim(),
    email: values.email.trim(),
    education_level: values.education_level as ProfileCreate['education_level'],
    education_field: values.education_field.trim() || null,
    experience_years: values.experience_years,
    experience_areas: values.experience_areas,
    skills: values.skills,
    languages: languages as ProfileCreate['languages'],
    preferred_locations: values.preferred_locations,
    career_interests: values.career_interests,
    work_authorisation:
      workAuthorisation as ProfileCreate['work_authorisation'],
    citizenship: values.citizenship.trim() || null,
    currently_enrolled: values.currently_enrolled,
  }
}

// ---------------------------------------------------------------------------
// Taxonomy-driven option lists
// ---------------------------------------------------------------------------

export interface TaxonomyOptions {
  degreeLevels: { label: string; value: string }[]
  languageLevels: { label: string; value: string }[]
  languages: string[]
  countries: string[]
  skills: string[]
  tracks: string[]
}

export function taxonomyToOptions(taxonomy: TaxonomyRead): TaxonomyOptions {
  return {
    degreeLevels: taxonomy.degree_levels.map((level) => ({
      value: level.value,
      label: level.label,
    })),
    languageLevels: taxonomy.language_levels
      .filter((level) => level.value !== 'not_spoken')
      .map((level) => ({ value: level.value, label: level.label })),
    languages: taxonomy.languages,
    countries: taxonomy.countries.map((country) => country.name),
    skills: taxonomy.skills,
    tracks: taxonomy.career_tracks,
  }
}
