# Claude Code

Claude Code memakai konfigurasi bergaya Anthropic via environment variables.

## Syarat

- Node.js 18+
- `npm install -g @anthropic-ai/claude-code@latest`

## Konfigurasi

```powershell
# Windows PowerShell
$env:ANTHROPIC_AUTH_TOKEN="API_KEY_KAMU"
$env:ANTHROPIC_BASE_URL="https://agentrouter.org"
$env:ANTHROPIC_MODEL="claude-opus-5"
```

```bash
# macOS / Linux
export ANTHROPIC_AUTH_TOKEN="API_KEY_KAMU"
export ANTHROPIC_BASE_URL="https://agentrouter.org"
export ANTHROPIC_MODEL="claude-opus-5"
```

| Variabel | Isi |
|---|---|
| `ANTHROPIC_AUTH_TOKEN` | API key provider (dikirim sebagai Bearer token) |
| `ANTHROPIC_BASE_URL` | Base URL **tanpa** `/v1` |
| `ANTHROPIC_MODEL` | Model default |

## Tes

```bash
claude
# ketik: hanya balas OK
```

## Catatan

- Base URL **tanpa** `/v1` — jangan campur dengan format OpenAI.
- Jika pernah login Claude Pro/Max/Team, env var di atas menimpa login langganan. Untuk kembali: `unset ANTHROPIC_AUTH_TOKEN ANTHROPIC_BASE_URL ANTHROPIC_MODEL`.
