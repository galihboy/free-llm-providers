# AgentRouter 🆓

> 🔄 Standalone script: sinkron dengan `formats/` per 2026-10-29
> ℹ️ Provider ini juga tersedia via framework: `python run.py --provider agentrouter`

**AgentRouter** (https://ps.air-outer.com) adalah router LLM dengan free credit. Pada pengujian 2026-10-29, GPT tersedia melalui Anthropic Messages dan OpenAI Responses; Chat Completions tidak didukung untuk model GPT.

## Info Dasar

| | |
|---|---|
| Website / Daftar | https://ps.air-outer.com |
| Ambil API key | dashboard Agent Router |
| Kuota gratis | credit awal $150-200 |
| Docs | https://ps.air-outer.com/docs/ |

> 💡 **Referral disclosure**: tautan pendaftaran AgentRouter di dokumen ini adalah link afiliasi (referral). Jika kamu mendaftar lewat sana, penulis mendapat reward **$50** dan kamu juga dapat **$50** (tanpa biaya ekstra). Reward ditransfer ke saldo akun via fitur *transfer*. Mau netral? Pakai https://agentrouter.org/register.

## Model Terlihat di Katalog (per 2026-10-29)

| Model | Format | Vision | Tool Calling | Max Input | Max Output | Catatan |
|---|---|---|---|---|---|---|
| `gpt-6.1-sol` | Anthropic + Responses | belum diklaim | belum diklaim | belum diklaim | belum diklaim | baru; teruji 200/OK |
| `gpt-6-astra` | Anthropic + Responses | belum diklaim | belum diklaim | belum diklaim | belum diklaim | teruji 200/OK |
| `gpt-5.6-sol` | Anthropic + Responses | belum diklaim | belum diklaim | belum diklaim | belum diklaim | teruji 200/OK |

> ⚠️ `claude-opus-4-6` dan `claude-opus-4-7` sudah **dihapus** dari AgentRouter.
> ⚠️ `deepseek-v4-flash` adalah model reasoning: `max_tokens` kecil (mis. 32) membuat jawaban kosong karena token habis untuk reasoning — pakai `-t 1024` atau lebih.
> ℹ️ Spek token/vision/tool-calling disinkronkan dari konfigurasi VS Code Copilot yang teruji (`chatLanguageModels.json`).

## Endpoint yang Teruji

| Format | Base URL | Endpoint |
|---|---|---|
| Anthropic Messages | `https://ps.air-outer.com` | `/v1/messages` |
| OpenAI Responses | `https://ps.air-outer.com/v1` | `/responses` |

> `/v1/chat/completions` diuji pada kedua domain dan mengembalikan HTTP 400: model GPT meminta `/v1/responses`.

## Cara Pakai (Standalone)

```bash
# 1. Isi .env di folder ini (atau root repo)
AGENTROUTER_API_KEY=sk-xxxxx

# 2. Chat via format OpenAI (model GPT)
python chat_openai.py -m gpt-6.1-sol -p "jelaskan LLM dalam 1 kalimat"

# 3. Chat via format Anthropic (model Claude)
python chat_anthropic.py -m gpt-6.1-sol -p "halo, apa kabar?"

# 4. List model
python chat_openai.py --list-models
```

## ⚠️ Gotcha (WAJIB BACA)

1. **Fingerprint client** — Server mem-fingerprint identitas client. Header `user-agent: claude-cli/...` + `x-stainless-*` **wajib ada**, kalau tidak → `401 unauthorized client detected` (ini bukan masalah key!).
2. **Moderasi bahasa** — Prompt non-Inggris kena `400 content-blocked`. Solusi: `ENGLISH_ANCHOR` di-prepend sebagai user message + assistant acknowledgment (sudah tertanam di script).
3. **Arti error**:
   - `401` = fingerprint header kurang
   - `403` = key valid tapi model tidak diizinkan
   - `400 content-blocked` = prompt kena moderasi bahasa
   - `402 Budget pool quota has been exhausted` = kuota budget pool akun habis; pilih budget pool lain / minta admin naikkan limit di console (bukan masalah key/fingerprint)
   - `503 无可用渠道 (no available channel)` = gateway AgentRouter tidak punya channel upstream; pada 2026-10-29 terjadi pada Claude Opus 5/4-8, GLM 5.3, dan DeepSeek V4 Flash
   - `400` pada `/v1/chat/completions` = model GPT meminta `/v1/responses`
4. **Dua key**: key lama (`AGENTROUTER_API_KEY`) bisa semua model di kedua endpoint; key baru (`AGENTROUTER_API_KEY_OPENAI`) hanya `gpt-5.6-sol`.
5. **Status ketersediaan dinamis** — pada 2026-10-29 `/v1/models` hanya mengembalikan tiga GPT; ketiganya berhasil via `/v1/messages`, dan `gpt-6.1-sol` juga via `/v1/responses`. Klaim credit top-up tidak membuktikan saldo akun terisi.

## Integrasi Tools Coding

Lihat [integrasi.md](integrasi.md) untuk cara pasang di VS Code Copilot, OpenCode, Claude Code, dan Codex.
