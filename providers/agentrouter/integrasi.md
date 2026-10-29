# Integrasi AgentRouter ke Tools Coding

AgentRouter mendukung 2 format, jadi cara pasangnya tergantung tool:

| Tool | Format | Base URL |
|---|---|---|
| VS Code GitHub Copilot | OpenAI (via **proxy lokal**) | `http://localhost:5099/v1` |
| OpenCode | Anthropic atau OpenAI-compatible | sesuai format |
| Claude Code | Anthropic | `https://ps.air-outer.com` (tanpa /v1) |
| Codex | OpenAI Responses | `https://ps.air-outer.com/v1` |
| Cursor | OpenAI Responses | `https://ps.air-outer.com/v1` |

> Sumber: https://ps.air-outer.com/docs/ — uji 2026-10-29 menunjukkan GPT menolak Chat Completions (400), tetapi menerima Responses dan Anthropic Messages.

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
- Model ID: `gpt-6.1-sol`, `gpt-6-astra`, atau `gpt-5.6-sol`

## 2. OpenCode

Buat `opencode.json` di project (pilih salah satu):

**Anthropic (Claude):**
```json
{
  "provider": {
    "agentrouter": {
      "npm": "@ai-sdk/anthropic",
      "options": { "baseURL": "https://ps.air-outer.com" },
      "models": { "gpt-6.1-sol": { "name": "gpt-6.1-sol" } }
    }
  },
  "model": "agentrouter/gpt-6.1-sol"
}
```

**OpenAI Compatible (GPT):**
```json
{
  "provider": {
    "agentrouter": {
      "npm": "@ai-sdk/openai-compatible",
      "options": { "baseURL": "https://ps.air-outer.com/v1" },
      "models": { "gpt-6.1-sol": { "name": "gpt-6.1-sol" } }
    }
  },
  "model": "agentrouter/gpt-6.1-sol"
}
```

Lalu: `opencode providers login --provider agentrouter` → masukkan API key.

## 3. Claude Code

```powershell
# Windows PowerShell
$env:ANTHROPIC_AUTH_TOKEN="API_KEY_KAMU"
$env:ANTHROPIC_BASE_URL="https://ps.air-outer.com"
$env:ANTHROPIC_MODEL="gpt-6.1-sol"
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
base_url = "https://ps.air-outer.com/v1"
wire_api = "responses"
experimental_bearer_token = "API_KEY_KAMU"
```

## 5. Cursor

Settings → Models → isi **OpenAI API Key** dengan API key AgentRouter → gunakan Responses API dan base URL `https://ps.air-outer.com/v1`.

> ⚠️ Keterbatasan Cursor: user gratis hanya bisa mode `auto`, tidak bisa pilih model manual.
> ⚠️ **Belum diverifikasi**: AgentRouter mem-fingerprint client (butuh header `claude-cli`). Jika Cursor mengirim user-agent miliknya sendiri, kemungkinan kena `401 unauthorized client` seperti VS Code Copilot — solusinya sama: pakai proxy lokal.
