import { defineConfig } from 'kubb/config'
import { adapterOas } from '@kubb/adapter-oas'
import { pluginTs } from '@kubb/plugin-ts'
import { pluginZod } from '@kubb/plugin-zod'
import { pluginAxios } from '@kubb/plugin-axios'
import { pluginReactQuery } from '@kubb/plugin-react-query'

/**
 * API client generation from the backend's live OpenAPI document.
 *
 * Requires the backend running on :8000
 * (`cd backend && uv run uvicorn app.main:app --reload --port 8000`):
 *     npm run gen:api
 *
 * `baseURL` is the origin only — FastAPI mounts everything under /api/v1, so
 * the spec paths already carry the prefix. Override for another environment
 * with API_BASE_URL before regenerating.
 */
const baseURL = process.env.API_BASE_URL ?? 'http://localhost:8000'

export default defineConfig({
  input: 'http://localhost:8000/api/v1/openapi.json',
  output: { path: './src/gen', clean: true },
  // Profile ids and pagination params as `number`, not bigint.
  adapter: adapterOas({ integerType: 'number' }),
  plugins: [
    pluginTs({ output: { path: 'types' } }),
    pluginZod({ output: { path: 'zod' }, inferred: true }),
    pluginAxios({
      output: { path: 'clients' },
      baseURL,
      // Calls resolve to the response body (the ApiResponse envelope).
      returnType: 'data',
      group: { type: 'tag' },
    }),
    pluginReactQuery({
      output: { path: 'queries' },
      client: 'axios',
      hooks: true,
      group: { type: 'tag' },
    }),
  ],
})
