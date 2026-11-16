import { QueryClient } from '@tanstack/react-query'

export function getContext() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        // The API layer is generated and typed; a single retry smooths over
        // dev-server hiccups without hiding real errors.
        staleTime: 30_000,
        retry: 1,
        refetchOnWindowFocus: false,
      },
    },
  })

  return {
    queryClient,
  }
}
export default function TanstackQueryProvider() {}
