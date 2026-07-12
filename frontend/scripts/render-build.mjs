import { spawnSync } from 'node:child_process'

const backendHost = process.env.BACKEND_EXTERNAL_HOSTNAME
if (!process.env.VITE_API_BASE_URL && backendHost) {
  process.env.VITE_API_BASE_URL = `https://${backendHost}/api/v1`
}
if (!process.env.VITE_WS_BASE_URL && backendHost) {
  process.env.VITE_WS_BASE_URL = `wss://${backendHost}`
}

const result = spawnSync('npm', ['run', 'build'], {
  env: process.env,
  shell: true,
  stdio: 'inherit',
})

process.exit(result.status ?? 1)
