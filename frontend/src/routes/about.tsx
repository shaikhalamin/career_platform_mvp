import { createFileRoute, Link } from '@tanstack/react-router'
import { ListChecks, Scale, ScanSearch, ShieldCheck } from 'lucide-react'

import { PageHeader } from '#/components/page-header'

export const Route = createFileRoute('/about')({ component: AboutPage })

const STEPS = [
  {
    icon: ListChecks,
    title: 'Normalization',
    desc: (
      <>
        Your free-text skills and interests are mapped onto a curated taxonomy
        (so “MS Excel” and “Excel” are one skill); degrees and language
        proficiencies become ranked values (bachelors = 4, professional English
        = 3 …); countries and work-authorisation states are validated. “Unknown”
        is preserved as a first-class value.
      </>
    ),
  },
  {
    icon: ScanSearch,
    title: 'Vector retrieval (FAISS, in-memory)',
    desc: (
      <>
        Profiles and opportunities become fixed-length feature vectors (skills,
        career tracks, countries, languages, degree, years). An exact
        cosine-similarity index narrows the catalogue to your top-K candidates
        before scoring.
      </>
    ),
  },
  {
    icon: Scale,
    title: 'Six-part weighted score (100 points)',
    desc: (
      <>
        Skills 35 (80% required + 20% optional coverage) · Experience 20 (years
        window + area overlap) · Education 15 (level + field relevance) ·
        Location 15 (preferred country 15 / same region 8) · Language 10
        (proficiency ratio per required language) · Interests 5. Each dimension
        reports matched and missing items.
      </>
    ),
  },
  {
    icon: ShieldCheck,
    title: 'Evidence-based eligibility (separate from score)',
    desc: (
      <>
        Hard constraints — mandatory languages, strict degree/experience, local
        work authorisation, citizenship, enrollment — are evaluated with
        explicit evidence. Unknowns become <em>requires verification</em> flags;
        failures rank below clean matches but always stay visible with their
        reasons.
      </>
    ),
  },
] as const

function AboutPage() {
  return (
    <main className="page-wrap max-w-3xl py-12">
      <PageHeader
        eyebrow="Under the hood"
        title="How matching works"
        description="PathPilot is fully offline and rule-based — no LLMs, no embedding models, no third-party AI inference. Every recommendation is a deterministic pipeline you can audit end to end."
      />

      <ol className="m-0 list-none space-y-0 p-0">
        {STEPS.map((step, index) => (
          <li key={step.title} className="relative flex gap-5 pb-10 last:pb-0">
            {/* Timeline rail */}
            {index < STEPS.length - 1 && (
              <span
                aria-hidden
                className="absolute top-12 left-[1.375rem] h-[calc(100%-3rem)] w-px bg-[var(--divider)]"
              />
            )}
            <span
              aria-hidden
              className="relative z-10 inline-flex size-11 shrink-0 items-center justify-center rounded-xl border border-[color-mix(in_oklab,var(--primary)_25%,var(--divider))] bg-[var(--primary-tint)] text-[var(--primary)]"
            >
              <step.icon className="size-5" />
            </span>
            <div className="panel-card min-w-0 flex-1 p-5">
              <p className="m-0 mb-1 text-xs font-semibold tracking-wider text-[var(--ink-tertiary)] uppercase">
                Step {index + 1}
              </p>
              <h2 className="m-0 mb-2 text-base font-semibold tracking-tight text-[var(--ink)]">
                {step.title}
              </h2>
              <p className="m-0 text-sm leading-relaxed text-[var(--ink-secondary)]">
                {step.desc}
              </p>
            </div>
          </li>
        ))}
      </ol>

      <div
        role="note"
        className="mt-10 flex gap-3 rounded-xl border border-dashed border-[var(--dashed-border)] bg-[var(--canvas-soft)] px-5 py-4 text-xs leading-relaxed text-[var(--ink-secondary)]"
      >
        <ShieldCheck
          aria-hidden
          className="mt-0.5 size-4 shrink-0 text-[var(--status-warning)]"
        />
        <p className="m-0">
          Eligibility output is automated guidance based on your stated profile.
          It is <strong>not a legal determination</strong> of visa or
          work-authorisation entitlement. Anything marked “requires
          verification” must be confirmed with the employer or the relevant
          authorities. See{' '}
          <Link to="/" className="underline">
            the product
          </Link>{' '}
          for what the scores cover.
        </p>
      </div>
    </main>
  )
}
