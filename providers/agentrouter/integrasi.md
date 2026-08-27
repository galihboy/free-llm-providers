# Integrasi AgentRouter ke Tools Coding

AgentRouter mendukung 2 format, jadi cara pasangnya tergantung tool:

| Tool | Format | Base URL |
|---|---|---|
| VS Code GitHub Copilot | OpenAI (via **proxy lokal**) | `http://localhost:5099/v1` |
| OpenCode | Anthropic atau OpenAI-compatible | sesuai format |
| Claude Code | Anthropic | `https://agentrouter.org` (tanpa /v1) |
| Codex | OpenAI Responses | `https://agentrouter.org/v1` |
| Cursor | OpenAI | `https://agentrouter.org/v1` |

> Sumber: https://agentrouter.org/docs/ — jangan campur base URL Anthropic (tanpa `/v1`) dengan OpenAI (pakai `/v1`).

## 1. VS Code GitHub Copilot

> ⚠️ **WAJIB pakai proxy lokal** — Copilot **tidak bisa** menembak AgentRouter langsung.
>
> **Bukti empiris** (2026-08-27): request TANPA fingerprint header `claude-cli` → `401 unauthorized client detected`; DENGAN fingerprint → `200 OK`. Copilot mengirim user-agent miliknya sendiri yang tidak bisa dikustomisasi, jadi selalu kena 401.
>
> **Alasan lain** (selain fingerprint): Copilot menyisipkan system prompt raksasa (~150-200KB) yang kena `content-blocked`, dan memakai format OpenAI (`tool_calls`) yang tidak cocok dengan Claude (butuh `tool_use`).
>
> **Solusi**: jalankan proxy dulu, lalu arahkan Copilot ke `http://localhost:5099`. Panduan lengkap (4 alasan teknis + langkah + contoh `chatLanguageModels.json`): lihat [`integrations/vscode-copilot.md`](../../integrations/vscode-copilot.md).

```bash
# 1. Jalankan proxy (biarkan terminal tetap terbuka)
pip install flask
python tools/proxy_openai_to_anthropic.py
```

Lalu di Copilot Chat → **Manage Models** → **Add Model** → **Custom Endpoint**:
- Group: `AgentRouter (Proxy)`, API Key: isi apa saja (key asli dibaca proxy dari `.env`)
- API format: **OpenAI Chat Completions**
- Base URL: `http://localhost:5099/v1`
- Model ID: `claude-opus-5`, `claude-opus-4-8`, `gpt-5.6-sol`, `glm-5.3`, atau `deepseek-v4-flash`

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
> ⚠️ **Belum diverifikasi**: AgentRouter mem-fingerprint client (butuh header `claude-cli`). Jika Cursor mengirim user-agent miliknya sendiri, kemungkinan kena `401 unauthorized client` seperti VS Code Copilot — solusinya sama: pakai proxy lokal.
