import { Link } from '@tanstack/react-router'
import { Compass } from 'lucide-react'

export default function Footer() {
  const year = new Date().getFullYear()

  return (
    <footer className="mt-24 bg-[var(--footer)] px-4 pb-10 pt-12 text-[var(--footer-link)]">
      <div className="page-wrap">
        <div className="flex flex-col gap-8 sm:flex-row sm:items-start sm:justify-between">
          <div className="max-w-xl">
            <p className="m-0 flex items-center gap-2 text-sm font-semibold tracking-tight text-white">
              <span
                aria-hidden
                className="inline-flex size-6 items-center justify-center rounded-md bg-[var(--primary)] text-[var(--on-primary)]"
              >
                <Compass className="size-3.5" />
              </span>
              PathPilot
            </p>
            <p className="mt-3 text-xs leading-relaxed">
              Recommendations and eligibility notes are automated guidance based
              on user-stated profiles. They are not a legal determination of
              visa or work-authorisation entitlement; items marked “requires
              verification” must be confirmed with the employer or the relevant
              authorities.
            </p>
          </div>
          <nav aria-label="Footer" className="text-xs">
            <ul className="m-0 grid list-none grid-cols-2 gap-x-10 gap-y-2 p-0">
              <li>
                <Link
                  to="/"
                  className="text-[var(--footer-link)] no-underline hover:text-white hover:underline"
                >
                  Home
                </Link>
              </li>
              <li>
                <Link
                  to="/recommendations"
                  className="text-[var(--footer-link)] no-underline hover:text-white hover:underline"
                >
                  Recommendations
                </Link>
              </li>
              <li>
                <Link
                  to="/opportunities"
                  className="text-[var(--footer-link)] no-underline hover:text-white hover:underline"
                >
                  Opportunities
                </Link>
              </li>
              <li>
                <Link
                  to="/shortlist"
                  className="text-[var(--footer-link)] no-underline hover:text-white hover:underline"
                >
                  Shortlist
                </Link>
              </li>
              <li>
                <Link
                  to="/profiles"
                  className="text-[var(--footer-link)] no-underline hover:text-white hover:underline"
                >
                  Profiles
                </Link>
              </li>
              <li>
                <Link
                  to="/about"
                  className="text-[var(--footer-link)] no-underline hover:text-white hover:underline"
                >
                  How it works
                </Link>
              </li>
            </ul>
          </nav>
        </div>
        <div className="mt-8 flex flex-col items-start justify-between gap-2 border-t border-[var(--footer-divider)] pt-5 text-xs sm:flex-row">
          <p className="m-0">
            &copy; {year} PathPilot — career mobility prototype. All
            organisations and opportunities are fictional.
          </p>
          <p className="m-0 font-medium text-slate-300">
            Rule-based matching · FAISS retrieval · no AI inference
          </p>
        </div>
      </div>
    </footer>
  )
}
