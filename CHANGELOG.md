# Changelog

Semua perubahan penting pada proyek ini dicatat di sini.
Format mengikuti [Keep a Changelog](https://keepachangelog.com/id/1.1.0/), versi mengikuti [Semantic Versioning](https://semver.org/lang/id/).

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
