import { Link, createFileRoute } from '@tanstack/react-router'
import {
  ArrowRight,
  BadgeCheck,
  Gauge,
  Layers,
  ListChecks,
  MapPin,
  SearchCheck,
  ShieldCheck,
  Star,
  UserRoundPlus,
} from 'lucide-react'

import { Button } from '#/components/ui/button'
import { Badge } from '#/components/ui/badge'
import { ScoreGauge } from '#/components/score-gauge'
import { useActiveProfile } from '#/lib/active-profile'
import { useGetProfileApiV1ProfilesProfileIdGet } from '#/gen/queries/profiles/useGetProfileApiV1ProfilesProfileIdGet'
import { useGetTaxonomyApiV1MetaTaxonomyGet } from '#/gen/queries/meta/useGetTaxonomyApiV1MetaTaxonomyGet'

export const Route = createFileRoute('/')({ component: HomePage })

const FEATURES = [
  {
    icon: Gauge,
    title: 'Six-part score',
    desc: 'Skills 35 · Experience 20 · Education 15 · Location 15 · Language 10 · Interests 5 — every point traceable.',
  },
  {
    icon: Layers,
    title: 'Vector retrieval',
    desc: 'Rule-generated feature vectors and in-memory FAISS cosine similarity narrow 50 roles to your top matches.',
  },
  {
    icon: SearchCheck,
    title: 'Evidence-based eligibility',
    desc: 'Hard constraints checked separately from scoring — with reasons, never silently satisfied.',
  },
  {
    icon: ShieldCheck,
    title: 'Honest unknowns',
    desc: "Unknown work authorisation or citizenship is labelled 'requires verification', never presented as confirmed.",
  },
] as const

const STEPS = [
  {
    icon: UserRoundPlus,
    title: 'Create a profile',
    desc: 'Describe your education, experience, skills, languages and where you want to work.',
  },
  {
    icon: ListChecks,
    title: 'Get ranked matches',
    desc: 'Every opportunity is scored and explained — strengths, gaps and eligibility evidence included.',
  },
  {
    icon: Star,
    title: 'Shortlist & verify',
    desc: 'Save the roles you like; anything uncertain is flagged for verification, never guessed.',
  },
] as const

function HomePage() {
  const { activeProfileId } = useActiveProfile()
  const profileQuery = useGetProfileApiV1ProfilesProfileIdGet(
    {
      path: { profile_id: activeProfileId ?? 0 },
    },
    { query: { enabled: activeProfileId !== null } },
  )
  const taxonomy = useGetTaxonomyApiV1MetaTaxonomyGet()
  const profile = profileQuery.data?.data

  return (
    <main>
      {/* Hero */}
      <section className="page-wrap grid items-center gap-10 px-0 py-16 sm:py-20 lg:grid-cols-[1.15fr_0.85fr] lg:gap-16">
        <div className="rise-in">
          <Badge variant="secondary" className="mb-5 gap-1.5 px-3 py-1 text-xs">
            <MapPin aria-hidden className="size-3.5" />
            International career mobility
          </Badge>
          <h1 className="display-title m-0 max-w-2xl text-4xl leading-[1.08] sm:text-5xl lg:text-6xl">
            Find where your profile travels best.
          </h1>
          <p className="mt-5 max-w-xl text-base leading-relaxed text-[var(--ink-secondary)] sm:text-lg">
            PathPilot compares your education, experience, skills, languages and
            location preferences against 50 international opportunities — then
            explains every point of every match, and flags anything that needs
            verification instead of guessing.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            {profile ? (
              <>
                <Button asChild size="lg">
                  <Link to="/recommendations">
                    View {profile.name}'s recommendations
                    <ArrowRight aria-hidden />
                  </Link>
                </Button>
                <Button asChild size="lg" variant="outline">
                  <Link
                    to="/profiles/$profileId/edit"
                    params={{ profileId: String(profile.id) }}
                  >
                    Edit profile
                  </Link>
                </Button>
              </>
            ) : (
              <>
                <Button asChild size="lg">
                  <Link to="/profiles/new">
                    Create a career profile
                    <ArrowRight aria-hidden />
                  </Link>
                </Button>
                <Button asChild size="lg" variant="outline">
                  <Link to="/profiles">Use an existing profile</Link>
                </Button>
              </>
            )}
          </div>
        </div>

        {/* Product visual — a sample match card */}
        <div
          className="rise-in panel-card relative mx-auto w-full max-w-sm p-6"
          style={{ animationDelay: '120ms' }}
          aria-hidden
        >
          <div className="mb-5 flex items-center justify-between">
            <div>
              <p className="m-0 text-xs font-medium text-[var(--ink-tertiary)]">
                Sample match
              </p>
              <p className="m-0 text-sm font-semibold text-[var(--ink)]">
                Programme Officer · Berlin
              </p>
            </div>
            <Badge variant="success">
              <BadgeCheck aria-hidden className="size-3.5" />
              Eligible
            </Badge>
          </div>
          <div className="flex items-center justify-center">
            <ScoreGauge
              score={87}
              max={100}
              size="lg"
              label="Sample match score"
            />
          </div>
          <div className="mt-6 space-y-3">
            {[
              { label: 'Skills', pct: 91 },
              { label: 'Experience', pct: 78 },
              { label: 'Location', pct: 100 },
            ].map((dim) => (
              <div key={dim.label}>
                <div className="mb-1 flex items-baseline justify-between text-xs">
                  <span className="font-medium text-[var(--ink)]">
                    {dim.label}
                  </span>
                  <span className="tabular-nums text-[var(--ink-secondary)]">
                    {dim.pct}%
                  </span>
                </div>
                <div className="h-1.5 overflow-hidden rounded-full bg-[var(--panel)]">
                  <div
                    className="h-full rounded-full bg-[var(--primary)]"
                    style={{ width: `${dim.pct}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="border-y border-[var(--divider)] bg-[var(--canvas-soft)]">
        <div className="page-wrap py-14">
          <p className="tier-eyebrow mb-2 text-center">How it works</p>
          <h2 className="m-0 text-center text-2xl font-semibold tracking-tight text-[var(--ink)] sm:text-3xl">
            Three steps to your shortlist
          </h2>
          <ol className="m-0 mt-10 grid list-none gap-8 p-0 md:grid-cols-3 md:gap-6">
            {STEPS.map((step, index) => (
              <li
                key={step.title}
                className="relative flex flex-col items-center text-center md:items-start md:text-left"
              >
                {index < STEPS.length - 1 && (
                  <span
                    aria-hidden
                    className="absolute top-6 left-[calc(100%+0.75rem)] hidden h-px w-6 bg-[var(--dashed-border)] md:block"
                  />
                )}
                <span className="mb-4 inline-flex size-12 items-center justify-center rounded-xl bg-[var(--primary)] text-[var(--on-primary)]">
                  <step.icon className="size-5" />
                </span>
                <p className="m-0 mb-1 text-xs font-semibold tracking-wider text-[var(--ink-tertiary)] uppercase">
                  Step {index + 1}
                </p>
                <h3 className="m-0 text-base font-semibold text-[var(--ink)]">
                  {step.title}
                </h3>
                <p className="mt-1.5 max-w-xs text-sm leading-relaxed text-[var(--ink-secondary)]">
                  {step.desc}
                </p>
              </li>
            ))}
          </ol>
        </div>
      </section>

      {/* Features */}
      <section className="page-wrap py-16">
        <p className="tier-eyebrow mb-2">Why PathPilot</p>
        <h2 className="m-0 mb-8 max-w-xl text-2xl font-semibold tracking-tight text-[var(--ink)] sm:text-3xl">
          Matching you can audit, not a black box.
        </h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {FEATURES.map((feature, index) => (
            <article
              key={feature.title}
              className="panel-card is-interactive rise-in p-5"
              style={{ animationDelay: `${index * 90 + 80}ms` }}
            >
              <span
                aria-hidden
                className="mb-4 inline-flex size-10 items-center justify-center rounded-lg bg-[var(--primary-tint)] text-[var(--primary)]"
              >
                <feature.icon className="size-5" />
              </span>
              <h3 className="m-0 mb-2 text-base font-semibold text-[var(--ink)]">
                {feature.title}
              </h3>
              <p className="m-0 text-sm leading-relaxed text-[var(--ink-secondary)]">
                {feature.desc}
              </p>
            </article>
          ))}
        </div>
      </section>

      {/* Coverage stats */}
      {taxonomy.data?.data && (
        <section className="page-wrap pb-16">
          <div className="panel-card grid grid-cols-2 gap-px overflow-hidden bg-[var(--divider)] sm:grid-cols-5">
            {[
              [taxonomy.data.data.countries.length, 'Countries'],
              [taxonomy.data.data.skills.length, 'Canonical skills'],
              [taxonomy.data.data.career_tracks.length, 'Career tracks'],
              [taxonomy.data.data.languages.length, 'Languages'],
              [50, 'Seed opportunities'],
            ].map(([count, label]) => (
              <div
                key={label as string}
                className="flex flex-col items-center gap-1 bg-card px-4 py-6"
              >
                <span className="text-2xl font-semibold tabular-nums tracking-tight text-[var(--ink)]">
                  {count as number}
                </span>
                <span className="text-xs font-medium text-[var(--ink-tertiary)]">
                  {label as string}
                </span>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Closing CTA */}
      <section className="page-wrap pb-20">
        <div className="rounded-2xl bg-[var(--primary)] px-6 py-12 text-center sm:px-12">
          <h2 className="m-0 text-2xl font-semibold tracking-tight text-[var(--on-primary)] sm:text-3xl">
            Ready to see where you match?
          </h2>
          <p className="mx-auto mt-3 max-w-xl text-sm leading-relaxed text-[color-mix(in_oklab,var(--on-primary)_85%,transparent)] sm:text-base">
            It takes about three minutes to describe your background — no
            signup, no password, just a profile.
          </p>
          <Button
            asChild
            size="lg"
            variant="outline"
            className="mt-7 border-white/40 bg-transparent text-white hover:bg-white/10 hover:text-white"
          >
            <Link to={profile ? '/recommendations' : '/profiles/new'}>
              {profile ? 'View recommendations' : 'Create your profile'}
              <ArrowRight aria-hidden />
            </Link>
          </Button>
        </div>
      </section>
    </main>
  )
}
