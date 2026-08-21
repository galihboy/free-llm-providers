# Codex

Codex CLI memakai konfigurasi OpenAI Responses API via `~/.codex/config.toml`.

## Syarat

- Node.js 18+
- `npm install -g @openai/codex` (atau `pnpm install -g @openai/codex`)

## Konfigurasi

Buat/edit `~/.codex/config.toml`:

```toml
model = "gpt-5.6-sol"
model_provider = "agentrouter"

[model_providers.agentrouter]
name = "AgentRouter"
base_url = "https://agentrouter.org/v1"
wire_api = "responses"
experimental_bearer_token = "API_KEY_KAMU"
```

| Field | Isi |
|---|---|
| `model` | Model default (misal `gpt-5.6-sol`, `gpt-5.5`, `glm-5.2`) |
| `base_url` | Base URL **dengan** `/v1` |
| `wire_api` | `"responses"` (OpenAI Responses API) |
| `experimental_bearer_token` | API key provider |

## Tes

```bash
cd my-project
codex
# ketik: hanya balas OK
```

## Catatan

- Untuk provider Groq/sejenis, ganti `base_url` dan `model` sesuai — beberapa provider hanya mendukung `wire_api = "chat"` (Chat Completions), cek docs provider.
