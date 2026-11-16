import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react'
import type { ReactNode } from 'react'

import { getProfileApiV1ProfilesProfileIdGet } from '#/gen/clients/profiles/getProfileApiV1ProfilesProfileIdGet'
import { isResponseError } from '#/gen/.kubb/client'

/**
 * The active profile — no signup, multiple people can share the app by
 * switching between locally-remembered profiles (id persisted in
 * localStorage, profile data lives server-side).
 *
 * A remembered id can outlive its profile (fresh database after a re-clone,
 * profile deleted elsewhere), so it is verified against the API before it
 * is used — every profile-scoped query would otherwise 404 with it.
 */

const STORAGE_KEY = 'activeProfileId'

interface ActiveProfileContextValue {
  activeProfileId: number | null
  setActiveProfile: (id: number | null) => void
}

const ActiveProfileContext = createContext<ActiveProfileContextValue | null>(
  null,
)

function readStoredId(): number | null {
  if (typeof window === 'undefined') return null
  const raw = window.localStorage.getItem(STORAGE_KEY)
  const parsed = raw === null ? Number.NaN : Number(raw)
  return Number.isInteger(parsed) && parsed >= 1 ? parsed : null
}

/** True unless the user switched to another profile mid-verification. */
function isStillCurrent(id: number): boolean {
  return window.localStorage.getItem(STORAGE_KEY) === String(id)
}

export function ActiveProfileProvider({ children }: { children: ReactNode }) {
  const [activeProfileId, setActiveProfileId] = useState<number | null>(null)

  // Hydrate from localStorage after mount (SSR-safe). The remembered id is
  // only activated once the backend confirms the profile still exists; a
  // definitive 404 drops it instead of letting it fail every query that
  // carries it (e.g. the opportunities list).
  useEffect(() => {
    const storedId = readStoredId()
    if (storedId === null) return
    let disposed = false

    getProfileApiV1ProfilesProfileIdGet({ path: { profile_id: storedId } })
      .then(() => {
        if (!disposed && isStillCurrent(storedId)) setActiveProfileId(storedId)
      })
      .catch((error: unknown) => {
        if (disposed || !isStillCurrent(storedId)) return
        if (isResponseError(error) && error.status === 404) {
          // The profile is gone — forget it rather than fail every query
          // that carries it.
          window.localStorage.removeItem(STORAGE_KEY)
        } else {
          // Backend unreachable or server error — stay optimistic.
          setActiveProfileId(storedId)
        }
      })

    return () => {
      disposed = true
    }
  }, [])

  const setActiveProfile = useCallback((id: number | null) => {
    setActiveProfileId(id)
    if (typeof window === 'undefined') return
    if (id === null) {
      window.localStorage.removeItem(STORAGE_KEY)
    } else {
      window.localStorage.setItem(STORAGE_KEY, String(id))
    }
  }, [])

  const value = useMemo(
    () => ({ activeProfileId, setActiveProfile }),
    [activeProfileId, setActiveProfile],
  )

  return (
    <ActiveProfileContext.Provider value={value}>
      {children}
    </ActiveProfileContext.Provider>
  )
}

export function useActiveProfile(): ActiveProfileContextValue {
  const context = useContext(ActiveProfileContext)
  if (!context) {
    throw new Error(
      'useActiveProfile must be used within ActiveProfileProvider',
    )
  }
  return context
}
