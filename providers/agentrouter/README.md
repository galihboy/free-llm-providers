# AgentRouter 🆓

> 🔄 Standalone script: sinkron dengan `formats/` per 2026-09-23
> ℹ️ Provider ini juga tersedia via framework: `python run.py --provider agentrouter`

**AgentRouter** (https://agentrouter.org/register?aff=8NFb) adalah router LLM gratis dengan credit awal **$150-200**. Unik karena mendukung **2 format API sekaligus**: Anthropic Messages dan OpenAI Chat Completions.

## Info Dasar

| | |
|---|---|
| Website / Daftar | https://agentrouter.org/register?aff=8NFb |
| Ambil API key | https://agentrouter.org/console/token |
| Kuota gratis | credit awal $150-200 |
| Docs | https://agentrouter.org/docs/ |

> 💡 **Referral disclosure**: tautan pendaftaran AgentRouter di dokumen ini adalah link afiliasi (referral). Jika kamu mendaftar lewat sana, penulis mendapat reward **$50** dan kamu juga dapat **$50** (tanpa biaya ekstra). Reward ditransfer ke saldo akun via fitur *transfer*. Mau netral? Pakai https://agentrouter.org/register.

## Model Tersedia (per 2026-08-27)

| Model | Format | Vision | Tool Calling | Max Input | Max Output | Catatan |
|---|---|---|---|---|---|---|
| `claude-opus-5` | Anthropic + OpenAI | ✅ | ✅ | 1.000.000 | 128.000 | |
| `claude-opus-4-8` | Anthropic + OpenAI | ✅ | ✅ | 1.000.000 | 128.000 | |
| `gpt-5.6-sol` | Anthropic + OpenAI | ✅ | ✅ | 1.000.000 | 128.000 | bisa lewat kedua endpoint |
| `gpt-6-astra` | Anthropic + OpenAI | ✅ | ✅ | 1.000.000 | 128.000 | baru per 2026-09; chat+vision OK, tool calling OK, BUKAN model reasoning |
| `glm-5.3` | Anthropic + OpenAI | ❌ | ✅ | 1.048.576 | 131.072 | baru per 2026-08-27 |
| `deepseek-v4-flash` | Anthropic + OpenAI | ❌ | ✅ | 1.048.576 | 393.216 | baru per 2026-08-27; butuh `-t ≥1024` |

> ⚠️ `claude-opus-4-6` dan `claude-opus-4-7` sudah **dihapus** dari AgentRouter.
> ⚠️ `deepseek-v4-flash` adalah model reasoning: `max_tokens` kecil (mis. 32) membuat jawaban kosong karena token habis untuk reasoning — pakai `-t 1024` atau lebih.
> ℹ️ Spek token/vision/tool-calling disinkronkan dari konfigurasi VS Code Copilot yang teruji (`chatLanguageModels.json`).

## Dua Endpoint

| Format | Base URL | Endpoint |
|---|---|---|
| Anthropic Messages | `https://agentrouter.org` | `/v1/messages` |
| OpenAI Compatible | `https://agentrouter.org/v1` | `/chat/completions` |

## Cara Pakai (Standalone)

```bash
# 1. Isi .env di folder ini (atau root repo)
AGENTROUTER_API_KEY=sk-xxxxx

# 2. Chat via format OpenAI (model GPT)
python chat_openai.py -m gpt-5.6-sol -p "jelaskan LLM dalam 1 kalimat"

# 3. Chat via format Anthropic (model Claude)
python chat_anthropic.py -m claude-opus-5 -p "halo, apa kabar?"

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
   - `503 无可用渠道 (no available channel)` = gateway AgentRouter tidak punya channel upstream utk model tsb di group `default` — gangguan sementara sisi server, model belum tentu dihapus
4. **Dua key**: key lama (`AGENTROUTER_API_KEY`) bisa semua model di kedua endpoint; key baru (`AGENTROUTER_API_KEY_OPENAI`) hanya `gpt-5.6-sol`.
5. **Status ketersediaan dinamis** — daftar model di katalog/console bisa beda dengan yang bisa dipanggil realtime (resource pool per akun). Tes ulang 2026-09-23: hanya `deepseek-v4-flash` hidup; `claude-opus-5`/`claude-opus-4-8`/`gpt-6-astra` → 402 (kuota habis), `gpt-5.6-sol`/`glm-5.3` → 503 (no channel). Selalu cek `--list-models` + tes 1 prompt sebelum andalkan provider ini.

## Integrasi Tools Coding

Lihat [integrasi.md](integrasi.md) untuk cara pasang di VS Code Copilot, OpenCode, Claude Code, dan Codex.
