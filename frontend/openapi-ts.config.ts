import { defineConfig } from '@hey-api/openapi-ts'

export default defineConfig({
  client: '@hey-api/client-fetch',
  input: 'http://localhost:8000/api/openapi.json',
  output: {
    path: 'src/generated',
    format: 'prettier',
    lint: 'eslint',
  },
  types: {
    enums: 'javascript',
  },
})
