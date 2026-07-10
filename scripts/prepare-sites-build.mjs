import { cpSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs'

rmSync('dist', { recursive: true, force: true })
cpSync('frontend/dist', 'dist', { recursive: true })
mkdirSync('dist/server', { recursive: true })
mkdirSync('dist/.openai', { recursive: true })
const hosting = JSON.parse(readFileSync('.openai/hosting.json', 'utf8'))
writeFileSync(
  'dist/.openai/hosting.json',
  `${JSON.stringify({ project_id: hosting.project_id }, null, 2)}\n`,
)

writeFileSync('dist/server/index.js', `
export default {
  async fetch(request, env) {
    const assetResponse = await env.ASSETS.fetch(request)
    if (assetResponse.status !== 404) return assetResponse

    const url = new URL(request.url)
    url.pathname = '/index.html'
    return env.ASSETS.fetch(new Request(url, request))
  },
}
`.trimStart())
