import { Link, createFileRoute } from '@tanstack/react-router'

import { useActiveProfile } from '#/lib/active-profile'
import { useGetProfileApiV1ProfilesProfileIdGet } from '#/gen/queries/profiles/useGetProfileApiV1ProfilesProfileIdGet'
import { useGetTaxonomyApiV1MetaTaxonomyGet } from '#/gen/queries/meta/useGetTaxonomyApiV1MetaTaxonomyGet'

export const Route = createFileRoute('/')({ component: HomePage })

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
    <main className="page-wrap px-4 pb-8 pt-14">
      <section className="rise-in px-2 py-10 sm:px-6 sm:py-14">
        <p className="tier-eyebrow mb-3">International career mobility</p>
        <h1 className="display-title mb-5 max-w-3xl text-4xl leading-[1.08] tracking-tight sm:text-6xl">
          Find where your profile travels best.
        </h1>
        <p className="mb-8 max-w-2xl text-base text-[var(--ink-secondary)] sm:text-lg">
          PathPilot compares your education, experience, skills, languages and
          location preferences against 50 international opportunities — then
          explains every point of every match, and flags anything that needs
          verification instead of guessing.
        </p>
        <div className="flex flex-wrap gap-3">
          {profile ? (
            <>
              <Link to="/recommendations" className="pill-primary">
                View {profile.name}'s recommendations
              </Link>
              <Link
                to="/profiles/$profileId/edit"
                params={{ profileId: String(profile.id) }}
                className="pill-outline"
              >
                Edit profile
              </Link>
            </>
          ) : (
            <>
              <Link to="/profiles/new" className="pill-primary">
                Create a career profile
              </Link>
              <Link to="/profiles" className="pill-outline">
                Use an existing profile
              </Link>
            </>
          )}
        </div>
      </section>

      <section className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          [
            'Six-part score',
            'Skills 35 · Experience 20 · Education 15 · Location 15 · Language 10 · Interests 5 — every point traceable.',
          ],
          [
            'Vector retrieval',
            'Rule-generated feature vectors and in-memory FAISS cosine similarity narrow 50 roles to your top matches.',
          ],
          [
            'Evidence-based eligibility',
            'Hard constraints checked separately from scoring — with reasons, never silently satisfied.',
          ],
          [
            'Honest unknowns',
            "Unknown work authorisation or citizenship is labelled 'requires verification', never presented as confirmed.",
          ],
        ].map(([title, desc], index) => (
          <article
            key={title}
            className="panel-card feature-card rise-in p-5"
            style={{ animationDelay: `${index * 90 + 80}ms` }}
          >
            <h2 className="mb-2 text-base font-semibold text-[var(--ink)]">
              {title}
            </h2>
            <p className="m-0 text-sm text-[var(--ink-secondary)]">{desc}</p>
          </article>
        ))}
      </section>

      {taxonomy.data?.data && (
        <section className="panel-card mt-8 p-6">
          <p className="tier-eyebrow mb-2">Coverage</p>
          <div className="flex flex-wrap gap-x-8 gap-y-2 text-sm text-[var(--ink-secondary)]">
            <span>
              <strong className="text-[var(--ink)]">
                {taxonomy.data.data.countries.length}
              </strong>{' '}
              countries
            </span>
            <span>
              <strong className="text-[var(--ink)]">
                {taxonomy.data.data.skills.length}
              </strong>{' '}
              canonical skills
            </span>
            <span>
              <strong className="text-[var(--ink)]">
                {taxonomy.data.data.career_tracks.length}
              </strong>{' '}
              career tracks
            </span>
            <span>
              <strong className="text-[var(--ink)]">
                {taxonomy.data.data.languages.length}
              </strong>{' '}
              languages
            </span>
            <span>
              <strong className="text-[var(--ink)]">50</strong> seed
              opportunities
            </span>
          </div>
        </section>
      )}
    </main>
  )
}
