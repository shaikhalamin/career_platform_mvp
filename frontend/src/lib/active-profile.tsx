import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react'
import type { ReactNode } from 'react'

/**
 * The active profile — no signup, multiple people can share the app by
 * switching between locally-remembered profiles (id persisted in
 * localStorage, profile data lives server-side).
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

export function ActiveProfileProvider({ children }: { children: ReactNode }) {
  const [activeProfileId, setActiveProfileId] = useState<number | null>(null)

  // Hydrate from localStorage after mount (SSR-safe).
  useEffect(() => {
    setActiveProfileId(readStoredId())
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
