# Integrasi AgentRouter ke Tools Coding

AgentRouter mendukung 2 format, jadi cara pasangnya tergantung tool:

| Tool | Format | Base URL |
|---|---|---|
| VS Code GitHub Copilot | Anthropic (Claude) atau OpenAI (GPT) | sesuai format |
| OpenCode | Anthropic atau OpenAI-compatible | sesuai format |
| Claude Code | Anthropic | `https://agentrouter.org` (tanpa /v1) |
| Codex | OpenAI Responses | `https://agentrouter.org/v1` |
| Cursor | OpenAI | `https://agentrouter.org/v1` |

> Sumber: https://agentrouter.org/docs/ — jangan campur base URL Anthropic (tanpa `/v1`) dengan OpenAI (pakai `/v1`).

## 1. VS Code GitHub Copilot

1. Buka Copilot Chat → **Manage Models** → **Add Model** → **Custom Endpoint**.
2. Group: `AgentRouter`, masukkan API key.
3. Pilih API format:
   - **Claude** (claude-opus-5, claude-opus-4-8) → format **Messages**, Base URL `https://agentrouter.org`
   - **GPT** (gpt-5.6-sol) → format **Chat Completions**, Base URL `https://agentrouter.org/v1`
4. Tes: kirim "hanya balas OK".

## 2. OpenCode

Buat `opencode.json` di project (pilih salah satu):

**Anthropic (Claude):**
```json
{
  "provider": {
    "agentrouter": {
      "npm": "@ai-sdk/anthropic",
      "options": { "baseURL": "https://agentrouter.org" },
      "models": { "claude-opus-5": { "name": "claude-opus-5" } }
    }
  },
  "model": "agentrouter/claude-opus-5"
}
```

**OpenAI Compatible (GPT):**
```json
{
  "provider": {
    "agentrouter": {
      "npm": "@ai-sdk/openai-compatible",
      "options": { "baseURL": "https://agentrouter.org/v1" },
      "models": { "gpt-5.6-sol": { "name": "gpt-5.6-sol" } }
    }
  },
  "model": "agentrouter/gpt-5.6-sol"
}
```

Lalu: `opencode providers login --provider agentrouter` → masukkan API key.

## 3. Claude Code

```powershell
# Windows PowerShell
$env:ANTHROPIC_AUTH_TOKEN="API_KEY_KAMU"
$env:ANTHROPIC_BASE_URL="https://agentrouter.org"
$env:ANTHROPIC_MODEL="claude-opus-5"
claude
```

> Base URL **tanpa** `/v1`. Jika pernah login Claude Pro/Max, unset ketiga env var untuk kembali ke akun langganan.

## 4. Codex

Buat `~/.codex/config.toml`:
```toml
model = "gpt-5.6-sol"
model_provider = "agentrouter"

[model_providers.agentrouter]
name = "AgentRouter"
base_url = "https://agentrouter.org/v1"
wire_api = "responses"
experimental_bearer_token = "API_KEY_KAMU"
```

## 5. Cursor

Settings → Models → isi **OpenAI API Key** dengan API key AgentRouter → aktifkan **Override OpenAI Base URL** → `https://agentrouter.org/v1`.

> ⚠️ Keterbatasan Cursor: user gratis hanya bisa mode `auto`, tidak bisa pilih model manual.
