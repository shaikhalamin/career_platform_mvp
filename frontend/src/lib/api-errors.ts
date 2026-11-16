import { z } from 'zod'

import { isResponseError } from '#/gen/.kubb/client'

/**
 * The backend's `ErrorResponse` envelope (see backend/app/core/responses.py).
 * It is not part of the OpenAPI document — error responses only carry a
 * description — so the shape lives here instead of the generated code.
 */
const errorEnvelopeSchema = z.object({
  success: z.literal(false),
  error: z.object({
    code: z.string(),
    message: z.string(),
    details: z
      .array(
        z.object({
          field: z.string().nullable(),
          message: z.string(),
          code: z.string().nullable(),
        }),
      )
      .default([]),
  }),
})

export type FormErrors = {
  /** Top-level message (null when the error maps to specific fields). */
  form: string | null
  /** Field name → message, e.g. `{ email: 'Email is already registered.' }`. */
  fields: Record<string, string>
}

/**
 * Turn a failed mutation error (a Kubb `ResponseError` carrying the parsed
 * envelope body in `.data`) into field/form errors for TanStack Form.
 */
export function toFormErrors(error: unknown): FormErrors {
  const body = isResponseError(error) ? error.data : error
  const parsed = errorEnvelopeSchema.safeParse(body)

  if (!parsed.success) {
    return {
      form: error instanceof Error ? error.message : 'Request failed.',
      fields: {},
    }
  }

  const fields: Record<string, string> = {}
  for (const detail of parsed.data.error.details) {
    if (detail.field && !(detail.field in fields)) {
      fields[detail.field] = detail.message
    }
  }

  return {
    form: Object.keys(fields).length > 0 ? null : parsed.data.error.message,
    fields,
  }
}
