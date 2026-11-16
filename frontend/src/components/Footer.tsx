export default function Footer() {
  const year = new Date().getFullYear()

  return (
    <footer className="mt-20 bg-[var(--footer)] px-4 pb-10 pt-8 text-[var(--footer-link)]">
      <div className="page-wrap">
        <p className="m-0 text-xs leading-relaxed tracking-[-0.02em]">
          Recommendations and eligibility notes are automated guidance based on
          user-stated profiles. They are not a legal determination of visa or
          work-authorisation entitlement; items marked “requires verification”
          must be confirmed with the employer or the relevant authorities.
        </p>
        <div className="mt-4 flex flex-col items-start justify-between gap-2 border-t border-[var(--footer-divider)] pt-4 text-xs sm:flex-row">
          <p className="m-0">
            &copy; {year} PathPilot — career mobility prototype. All
            organisations and opportunities are fictional.
          </p>
          <p className="m-0 font-medium text-white">
            Rule-based matching · FAISS retrieval · no AI inference
          </p>
        </div>
      </div>
    </footer>
  )
}
