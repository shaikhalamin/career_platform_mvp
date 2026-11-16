import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/about')({ component: AboutPage })

function AboutPage() {
  return (
    <main className="page-wrap max-w-3xl py-12">
      <p className="tier-eyebrow mb-2">Under the hood</p>
      <h1 className="display-title m-0 text-3xl font-semibold tracking-tight">
        How matching works
      </h1>
      <p className="mt-3 text-sm leading-relaxed text-[var(--ink-secondary)]">
        PathPilot is fully offline and rule-based — no LLMs, no embedding
        models, no third-party AI inference. Every recommendation is a
        deterministic pipeline you can audit end to end.
      </p>

      <ol className="mt-8 m-0 list-none space-y-6 p-0">
        <li className="panel-card p-6">
          <h2 className="m-0 mb-2 text-base font-semibold">
            1 · Normalization
          </h2>
          <p className="m-0 text-sm text-[var(--ink-secondary)]">
            Your free-text skills and interests are mapped onto a curated
            taxonomy (so “MS Excel” and “Excel” are one skill); degrees and
            language proficiencies become ranked values (bachelors = 4,
            professional English = 3 …); countries and work-authorisation states
            are validated. “Unknown” is preserved as a first-class value.
          </p>
        </li>
        <li className="panel-card p-6">
          <h2 className="m-0 mb-2 text-base font-semibold">
            2 · Vector retrieval (FAISS, in-memory)
          </h2>
          <p className="m-0 text-sm text-[var(--ink-secondary)]">
            Profiles and opportunities become fixed-length feature vectors
            (skills, career tracks, countries, languages, degree, years). An
            exact cosine-similarity index narrows the catalogue to your top-K
            candidates before scoring.
          </p>
        </li>
        <li className="panel-card p-6">
          <h2 className="m-0 mb-2 text-base font-semibold">
            3 · Six-part weighted score (100 points)
          </h2>
          <p className="m-0 text-sm text-[var(--ink-secondary)]">
            Skills 35 (80% required + 20% optional coverage) · Experience 20
            (years window + area overlap) · Education 15 (level + field
            relevance) · Location 15 (preferred country 15 / same region 8) ·
            Language 10 (proficiency ratio per required language) · Interests 5.
            Each dimension reports matched and missing items.
          </p>
        </li>
        <li className="panel-card p-6">
          <h2 className="m-0 mb-2 text-base font-semibold">
            4 · Evidence-based eligibility (separate from score)
          </h2>
          <p className="m-0 text-sm text-[var(--ink-secondary)]">
            Hard constraints — mandatory languages, strict degree/experience,
            local work authorisation, citizenship, enrollment — are evaluated
            with explicit evidence. Unknowns become{' '}
            <em>requires verification</em> flags; failures rank below clean
            matches but always stay visible with their reasons.
          </p>
        </li>
      </ol>

      <p className="mt-8 rounded-md border border-dashed border-[var(--dashed-border)] bg-[var(--canvas-soft)] px-4 py-3 text-xs leading-relaxed text-[var(--ink-secondary)]">
        Eligibility output is automated guidance based on your stated profile.
        It is <strong>not a legal determination</strong> of visa or
        work-authorisation entitlement. Anything marked “requires verification”
        must be confirmed with the employer or the relevant authorities.
      </p>
    </main>
  )
}
