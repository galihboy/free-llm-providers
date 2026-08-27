# Changelog

Semua perubahan penting pada proyek ini dicatat di sini.
Format mengikuti [Keep a Changelog](https://keepachangelog.com/id/1.1.0/), versi mengikuti [Semantic Versioning](https://semver.org/lang/id/).

## [0.6.1] - 2026-08-27

### Diperbaiki
- **Poolside**: koreksi Max Input `laguna-xs-2.1` dari `1.048.576` (1M) menjadi `262.144` (256K). Context window resmi XS 2.1 = 256K tokens (docs.poolside.ai), sebelumnya salah copy dari baris Laguna S 2.1 di `chatLanguageModels.json`. File: `providers/poolside/README.md`.
- **AgentRouter**: koreksi skema reward referral dari "penulis $150, teman $50" menjadi "penulis $50, teman $50" (simetris). Per info terbaru AgentRouter: setiap teman yang diundang → kamu dapat $50, teman juga dapat $50; reward ditransfer ke saldo akun via fitur *transfer*. File: `README.md`, `providers/agentrouter/README.md`.
- **AgentRouter × VS Code Copilot**: `providers/agentrouter/integrasi.md` bagian "1. VS Code GitHub Copilot" ditulis ulang — sebelumnya mengesankan bisa ditembak langsung, padahal **wajib proxy lokal**. Bukti empiris 2026-08-27: request tanpa fingerprint header `claude-cli` → `401 unauthorized client detected`; dengan fingerprint → `200 OK`. Ditambah catatan kehati-hatian untuk Cursor (belum diverifikasi, potensi 401 yang sama).

## [0.6.0] - 2026-08-27

### Ditambahkan
- **Provider baru: Poolside** (https://poolside.ai) — free preview terbatas waktu via inference API OpenAI-compatible.
- `providers/poolside.yaml`: format `openai_chat` dengan model `poolside/laguna-s-2.1` (118B/8B MoE, 1M context) dan `poolside/laguna-xs-2.1` (33B/3B MoE, 256K context, reasoning).
- `providers/poolside/chat.py`: script standalone (mirror pola Groq — provider standar tanpa anchor).
- `providers/poolside/README.md`: info Gmail OAuth untuk API key, opt-out training, gotcha text-only & reasoning.
- `data/providers.json`: entri Poolside ditambahkan.
- `README.md`: baris Poolside di tabel provider.
- `.env.example`: blok `POOLSIDE_API_KEY=` + komentar cara buat via Gmail OAuth.

### Catatan Penting
- **TEXT-ONLY**: kedua model Poolside TIDAK mendukung multimodal (image/video/audio) → 400 `does not support multimodal`.
- **Reasoning model**: `laguna-xs-2.1` butuh `max_tokens ≥ 1024`; pakai `-t 32` → jawaban kosong (token habis untuk reasoning).
- **API key via Gmail OAuth**: login di https://platform.poolside.ai/api-keys dengan akun Google.
- **Opt-out training**: secara default konten dipakai training Poolside. Buka **Settings** → aktifkan **"Opt-out of Poolside using your Content for training"** SEBELUM mulai pakai kalau tidak setuju.
- **Free preview terbatas**: program gratis bisa berakhir sewaktu-waktu.

### Hasil Tes
- ✅ `--list-models` [LIVE]: 2 model (`poolside/laguna-s-2.1`, `poolside/laguna-xs-2.1`)
- ✅ `laguna-s-2.1` chat EN: 200 OK
- ✅ `laguna-s-2.1` chat ID: 200 OK (tidak ada moderasi bahasa)
- ✅ Vision test: 400 `does not support multimodal` (sesuai dokumentasi)
- ✅ `laguna-xs-2.1` reasoning: 122 reasoning_tokens untuk prompt "say OK"

## [0.5.0] - 2026-08-27

### Ditambahkan
- **2 model baru AgentRouter**: `glm-5.3` (1M input / 128K output) dan `deepseek-v4-flash` (1M input / 384K output) — tersedia di kedua endpoint (Anthropic + OpenAI), tool calling ✅, vision ❌.
- `providers/agentrouter.yaml`: kedua model ditambahkan ke `models:` format `anthropic_messages` dan `openai_chat` + gotcha baru.
- `providers/agentrouter/README.md`: tabel model kini memuat kolom Vision, Tool Calling, Max Input, Max Output (disinkronkan dari konfigurasi VS Code Copilot teruji).
- `integrations/vscode-copilot.md`: contoh entri `chatLanguageModels.json` diperbarui ke 5 model dengan spek token terbaru.

### Diubah
- Spek token model lama diperbarui sesuai konfigurasi teruji: `claude-opus-5`, `claude-opus-4-8`, `gpt-5.6-sol` kini 1M input / 128K output, vision ✅ ketiganya.

### Hasil Tes
- ✅ `--list-models` [LIVE] kedua endpoint: 5 model (claude-opus-4-8, claude-opus-5, deepseek-v4-flash, glm-5.3, gpt-5.6-sol)
- ✅ `glm-5.3` via openai_chat: 2171 ms, 98 token total
- ✅ `deepseek-v4-flash` via openai_chat (`-t 1024`): 1771 ms; dengan `-t 32` jawaban kosong (token habis untuk reasoning)

## [0.4.1] - 2026-08-20

### Ditambahkan
- **Anchor lokal per-provider**: folder `providers/<nama>/anchors/` kini didukung. Pencarian file anchor: lokal provider (menang) → global `anchors/` (fallback). Berguna untuk anchor yang spesifik satu provider.
- Contoh: `providers/agentrouter/anchors/vscode_coding.yaml` (persona coding ringkas untuk VS Code Copilot via proxy).
- `run.py`: `pick_format()` menyuntikkan `anchor_dirs`; `--list-anchors --provider <nama>` menampilkan anchor lokal provider juga.
- `tools/proxy_openai_to_anthropic.py`: `--anchor` kini menerima nama file lokal provider/global (registry → file lokal → file global → teks bebas).
- `anchors/README.md`: tambah bagian "Anchor lokal per-provider".

## [0.4.0] - 2026-08-20

### Ditambahkan
- Folder `anchors/`: anchor kini bisa disimpan di **file YAML terpisah** per tugas (`general`, `coding`, `extraction`, `text2sql`, `eval`, `custom_chat`) — tambah anchor baru cukup buat file baru, tanpa edit kode Python.
- `anchors/README.md`: panduan lengkap (cara pakai via CLI/YAML, cara buat anchor baru, tips, skenario VS Code).
- `formats/base.py`: `load_anchor_file()`, `list_anchor_files()`; `get_anchor()` kini mendukung `moderation.anchor_file` dengan prioritas: `anchor_text` > `anchor_file` > `english_anchor` (registry → fallback file).
- `run.py`: flag `--list-anchors`; `--anchor` kini menerima nama varian bawaan ATAU nama file di `anchors/` (misal `--anchor custom_chat`).
- `providers/agentrouter.yaml`: dokumentasi `moderation` diperbarui sesuai opsi baru.

## [0.3.1] - 2026-08-20

### Ditambahkan
- `integrations/vscode-copilot.md`: tambah **Cara B** — contoh entri `chatLanguageModels.json` lengkap untuk AgentRouter (Proxy) dengan 3 model, diambil dari konfigurasi yang terbukti jalan. Termasuk catatan field penting (`apiKey` dummy, `url` tanpa `/v1`, `toolCalling`, `maxOutputTokens`) dan gotcha blok `thinking` Claude.

## [0.3.0] - 2026-08-20

### Ditambahkan
- `tools/proxy_openai_to_anthropic.py`: proxy lokal Flask (OpenAI → Anthropic) untuk integrasi VS Code Copilot dengan provider berfingerprint (AgentRouter). Migrasi dari proxy teruji di repo eksperimen, kini baca config dari `providers/*.yaml` + dukung flag `--provider`, `--port`, `--anchor`.
- `integrations/vscode-copilot.md` ditulis ulang: 2 skenario (langsung vs proxy) + tabel 4 alasan teknis mengapa Copilot butuh proxy.
- `flask` masuk `requirements.txt` (opsional, hanya untuk proxy).

### Hasil Tes
- ✅ Proxy jalan di `localhost:5099`; request OpenAI-format → upstream Anthropic 200 → respons OpenAI-format valid
- ✅ `/v1/models` mengembalikan 3 model
- ⚠️ Catatan: `max_tokens` kecil (64) bisa menghasilkan `content: null` karena token habis untuk blok `thinking` Claude; pakai ≥1024

## [0.2.0] - 2026-08-20

### Diubah
- Anchor moderasi kini **bervarian per jenis tugas** (registry `ANCHORS` di `formats/base.py`): `general` (default baru), `coding`, `extraction`, `text2sql`, `eval`. Anchor lama yang bias coding tetap tersedia sebagai varian `coding`.
- Konfigurasi YAML diperluas: `moderation.english_anchor` menerima `true` (=general) atau nama varian; `moderation.anchor_text` untuk teks bebas.
- `run.py` menambah flag `--anchor <varian>` untuk override sementara tanpa edit YAML.
- Fungsi `needs_anchor()` dihapus, digantikan `get_anchor()` yang lebih fleksibel.

### Hasil Tes
- ✅ `--anchor extraction`: ekstraksi nama/kota → output JSON bersih
- ✅ `--anchor text2sql`: query SQL top-5 siswa → SQL valid

## [0.1.0] - 2026-08-20

### Ditambahkan
- Struktur awal repo: arsitektur format-first dengan 2 lapisan (standalone + framework terintegrasi).
- `formats/`: client reusable `openai_chat` dan `anthropic_messages`, plus `base.py` (extra_headers opsional, ENGLISH_ANCHOR, capability list_models live/statis).
- `run.py`: CLI universal multi-provider (`--provider`, `--format`, `--list-models`).
- `tools/smoke_test_all.py`: tes semua provider sekaligus → tabel + `smoke_result.json`.
- Provider **AgentRouter** (YAML + folder standalone: `chat_openai.py`, `chat_anthropic.py`, `integrasi.md`).
- Provider **Groq** (YAML + folder standalone `chat.py`) sebagai contoh provider standar tanpa keistimewaan.
- `integrations/`: panduan VS Code Copilot, OpenCode, Claude Code, Codex.
- `data/providers.json`: registry machine-readable.
- `CONTRIBUTING.md`: aturan sinkronisasi lapisan standalone vs framework.

### Temuan / Catatan
- AgentRouter: butuh fingerprint header `claude-cli` (tanpa itu 401 "unauthorized client"); prompt non-Inggris kena 400 `content-blocked` → solusi ENGLISH_ANCHOR.
- AgentRouter: model `claude-opus-4-6`/`4-7` sudah dihapus; tersisa `claude-opus-5`, `claude-opus-4-8`, `gpt-5.6-sol`.
- Groq: model lama (`llama-3.3-70b-versatile`) sudah 404; model aktual per 2026-08-20: `openai/gpt-oss-120b`, `openai/gpt-oss-20b`, `qwen/qwen3.6-27b`, `groq/compound-mini`.

### Hasil Tes
- ✅ AgentRouter openai_chat (`gpt-5.6-sol`), anthropic_messages (`claude-opus-5`), list-models [LIVE]
- ✅ Groq openai_chat (`openai/gpt-oss-120b`, ~1 detik)
- ✅ Script standalone AgentRouter & smoke test semua provider
