# Poolside 🆓

> 🔄 Standalone script: sinkron dengan `formats/` per 2026-08-27
> ℹ️ Provider ini juga tersedia via framework: `python run.py --provider poolside`

**Poolside** (https://poolside.ai) adalah lab AI yang fokus pada model bahasa untuk **software engineering**. Saat ini menyediakan **free preview terbatas waktu** untuk model Laguna via inference API OpenAI-compatible.

## Info Dasar

| | | |
|---|---|---|
| Website | https://poolside.ai |
| Daftar / Ambil API key | https://platform.poolside.ai/api-keys (login via **Gmail OAuth**) |
| Kuota gratis | free preview terbatas waktu (limited-time preview) |
| Format API | OpenAI Compatible |
| Docs | https://docs.poolside.ai |

> ⚠️ **Privasi data**: secara default, konten yang kamu kirim ke API akan dipakai untuk training Poolside. Jika tidak setuju, buka **Settings** dan aktifkan opsi **"Opt-out of Poolside using your Content for training"** SEBELUM mulai pakai.

## Model Populer (per 2026-08-27)

| Model | ID | Tipe | Vision | Tool Calling | Max Input | Max Output | Catatan |
|---|---|---|---|---|---|---|---|
| Laguna S 2.1 | `poolside/laguna-s-2.1` | chat | ❌ | ✅ | 1.048.576 | 32.768 | model utama (118B/8B MoE, 1M context) |
| Laguna XS 2.1 | `poolside/laguna-xs-2.1` | reasoning | ❌ | ✅ | 1.048.576 | 32.768 | lebih kecil & cepat (33B/3B MoE, 256K context); butuh `-t ≥1024` |

> ⚠️ `poolside/laguna-m.1` sudah **dihapus** (404) per 2026-08-27.
> ⚠️ Kedua model **TEXT-ONLY** — tidak mendukung image/video/audio. Kirim image akan dapat `400 "does not support multimodal"`.
> ⚠️ `laguna-xs-2.1` adalah model reasoning: `max_tokens` kecil (mis. 32) membuat jawaban kosong karena token habis untuk reasoning — pakai `-t 1024` atau lebih.
> ℹ️ Spek token/vision/tool-calling disinkronkan dari konfigurasi VS Code Copilot yang teruji (`chatLanguageModels.json`).

## Cara Pakai (Standalone)

```bash
# 1. Isi .env di folder ini (atau root repo)
POOLSIDE_API_KEY=poolside-xxxxx

# 2. Chat
python chat.py -m poolside/laguna-s-2.1 -p "jelaskan LLM dalam 1 kalimat"

# 3. List model
python chat.py --list-models
```

## ⚠️ Gotcha (WAJIB BACA)

1. **TEXT-ONLY** — kedua model tidak mendukung multimodal (image/video/audio). Kirim image akan dapat `400 "does not support multimodal"`.
2. **Reasoning model** — `laguna-xs-2.1` butuh `max_tokens ≥ 1024`. Pakai `-t 32` → jawaban kosong karena token habis untuk reasoning.
3. **API key via Gmail OAuth** — login ke https://platform.poolside.ai pakai akun Google, lalu buat key di halaman API Keys.
4. **Opt-out training** — secara default konten kamu dipakai training Poolside. Buka **Settings** dan aktifkan **"Opt-out of Poolside using your Content for training"** kalau tidak mau.
5. **Free preview terbatas** — program gratis bisa berakhir sewaktu-waktu; cek halaman resmi untuk status terkini.
