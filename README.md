# Free LLM Providers 🆓

[![Smoke Test](https://github.com/galihboy/free-llm-providers/actions/workflows/smoke.yml/badge.svg)](https://github.com/galihboy/free-llm-providers/actions/workflows/smoke.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> Dibuat oleh **Galih Hermawan** ([galih.eu](https://galih.eu)). Lisensi MIT — bebas dipakai & dimodifikasi.

Kurasi provider LLM **gratis** (atau free credit) yang sudah **dites langsung**, lengkap dengan contoh pemakaian dan integrasi ke tools coding (VS Code Copilot, OpenCode, Claude Code, Codex, dll).

> Semua script di repo ini menggunakan Python + `requests`. Tidak ada SDK wajib.

---

## Mulai dari mana?

```
┌─ Cuma butuh 1 provider? ──────→ providers/<nama>/README.md
│                                 (script standalone: copy, isi .env, jalan)
│
├─ Mau kelola banyak provider? ─→ run.py + providers/*.yaml
│                                 (framework terintegrasi, 1 CLI untuk semua)
│
└─ Mau pasang di tool coding? ──→ integrations/<tool>.md
                                  (Copilot, OpenCode, Claude Code, Codex, Cursor)
```

---

## Daftar Provider

| Provider | Kuota Gratis | Model | Format API | Status | Panduan |
|---|---|---|---|---|---|
| [AgentRouter](https://agentrouter.org) | credit $150-200 | claude-opus-5, claude-opus-4-8, gpt-5.6-sol | Anthropic + OpenAI | ✅ Aktif | [📖 providers/agentrouter](providers/agentrouter/) |
| [Groq](https://console.groq.com) | free tier (rate limit) | openai/gpt-oss-120b, openai/gpt-oss-20b, qwen/qwen3.6-27b, groq/compound-mini | OpenAI | ✅ Aktif | [📖 providers/groq](providers/groq/) |

> Kolom "Model" di atas hanya **contoh model chat teruji** (bukan daftar lengkap). Groq misalnya punya belasan model (termasuk whisper/guard). Untuk daftar **lengkap & terkini**, jalankan: `python run.py --provider <nama> --list-models` (fetch live dari API). Daftar model bisa berubah sewaktu-waktu — lihat [CHANGELOG.md](CHANGELOG.md).

> Status: ✅ aktif teruji · ⚠️ terbatas · ❌ error/down · 💰 butuh payment
> Provider lain menyusul — lihat [data/providers.json](data/providers.json) untuk registry lengkap.

---

## Quick Start (Framework Terintegrasi)

```bash
# 1. Install dependensi
pip install -r requirements.txt
#    (flask sudah termasuk tapi HANYA dibutuhkan untuk proxy VS Code;
#     kalau tidak pakai proxy, bisa di-skip: pip install requests python-dotenv PyYAML)

# 2. Salin template env dan isi API key kamu
copy .env.example .env     # Windows
# cp .env.example .env     # Linux/macOS

# 3. Chat via provider + format tertentu
python run.py --provider agentrouter --format openai_chat -m gpt-5.6-sol -p "jelaskan LLM"

# 4. List model yang tersedia
python run.py --provider agentrouter --list-models

# 5. Smoke test semua provider sekaligus
python tools/smoke_test_all.py
```

## Quick Start (Standalone — 1 Provider Saja)

```bash
cd providers/agentrouter
copy ..\..\.env.example .env   # isi AGENTROUTER_API_KEY
python chat_openai.py -m gpt-5.6-sol -p "halo"
```

---

## Struktur Repo

```
free-llm-providers/
├── README.md               # ← kamu di sini
├── run.py                  # CLI universal multi-provider
├── formats/                # Client reusable per format API
│   ├── base.py             # Helper: headers, anchor, parsing
│   ├── openai_chat.py      # POST /v1/chat/completions
│   └── anthropic_messages.py  # POST /v1/messages
├── providers/              # Config (YAML) + panduan standalone per provider
│   ├── agentrouter.yaml
│   ├── agentrouter/        # ← folder standalone (README + script mandiri)
│   ├── groq.yaml
│   └── groq/
├── integrations/           # Panduan pasang di tools coding
├── tools/
│   └── smoke_test_all.py   # Tes semua provider → tabel hasil
└── data/
    └── providers.json      # Registry machine-readable
```

## Konsep Penting

- **Format-first**: beda format API (OpenAI vs Anthropic) ditangani di `formats/`, bukan di tiap provider.
- **Capability opsional**: `extra_headers`, `english_anchor`, `list_models` hanya diisi kalau provider memang butuh. Default = paling sederhana.
- **Dua lapisan**: script standalone (mudah, copy & jalan) + framework terintegrasi (kelola banyak provider). Lihat [CONTRIBUTING.md](CONTRIBUTING.md) untuk aturan sinkronisasi.

## ⚠️ Keamanan

- File `.env` berisi API key **tidak boleh** di-commit (sudah di `.gitignore`).
- Repo ini hanya menyediakan `.env.example` (template tanpa nilai).
- Jika key kamu bocor, segera rotate di dashboard provider.

## Lisensi

[MIT](LICENSE) — bebas dipakai, dimodifikasi, dan dibagikan.

## Disclosure (Tautan Referral)

Beberapa tautan pendaftaran AgentRouter di repo ini adalah **referral link**. Jika kamu mendaftar lewat link tersebut, penulis mendapat reward credit tambahan (dan kamu juga dapat bonus) — **tanpa biaya ekstra** untukmu.

- Tautan referral: https://agentrouter.org/register?aff=8NFb
- Skema reward (per info resmi AgentRouter): undang teman → kamu dapat **$150**, teman dapat **$50**; reward ditransfer ke saldo akun lewat fitur *transfer*.
- Tidak suka referral? Pakai link biasa: https://agentrouter.org/register

## Pencatatan Perkembangan

- [CHANGELOG.md](CHANGELOG.md) — riwayat revisi per versi (apa yang berubah, temuan, hasil tes)
- [ROADMAP.md](ROADMAP.md) — progress provider & rencana pengembangan ke depan
