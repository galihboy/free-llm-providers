# OpenCode

OpenCode dikonfigurasi lewat `opencode.json` di root project. Mendukung 2 jenis provider: Anthropic dan OpenAI-compatible.

## Instalasi

```bash
# Windows (butuh Node.js)
npm install -g opencode-ai

# Linux/macOS
curl -fsSL https://opencode.ai/install | bash
```

## Konfigurasi — Provider Anthropic (misal Claude)

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "agentrouter": {
      "npm": "@ai-sdk/anthropic",
      "name": "AgentRouter (Anthropic)",
      "options": { "baseURL": "https://agentrouter.org" },
      "models": { "claude-opus-5": { "name": "claude-opus-5" } }
    }
  },
  "model": "agentrouter/claude-opus-5"
}
```

## Konfigurasi — Provider OpenAI Compatible (misal GPT/Groq)

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "groq": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Groq",
      "options": { "baseURL": "https://api.groq.com/openai/v1" },
      "models": { "openai/gpt-oss-120b": { "name": "openai/gpt-oss-120b" } }
    }
  },
  "model": "groq/openai/gpt-oss-120b"
}
```

## Login & Jalankan

```bash
opencode providers login --provider agentrouter   # masukkan API key
opencode
```

> Pilih salah satu blok konfigurasi (Anthropic ATAU OpenAI-compatible) sesuai format provider.
