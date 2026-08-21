# VS Code GitHub Copilot

GitHub Copilot mendukung **custom endpoint** dengan 2 format API. Namun ada batasan penting: **Copilot tidak bisa dikustomisasi header/payload-nya**, sehingga provider "rewel" (butuh fingerprint header, anchor, sanitasi) **tidak bisa ditembak langsung** — solusinya pakai **proxy lokal**.

## Dua Skenario

| Skenario | Provider contoh | Cara |
|---|---|---|
| Provider standar (tanpa fingerprint/moderasi) | Groq | Langsung custom endpoint |
| Provider rewel (fingerprint + moderasi) | AgentRouter | **Proxy lokal** (wajib) |

---

## Skenario 1: Langsung (Provider Standar)

1. Pastikan sudah login GitHub di VS Code (tanpa login, menu model tidak tersedia).
2. Buka panel Copilot Chat → **Manage Models** → **Add Model** → **Custom Endpoint**.
3. Isi:
   - **Group name**: nama bebas (misal `Groq`)
   - **API Key**: key dari provider
4. Pilih **API format**: OpenAI Chat Completions.
5. Isi **Base URL**: `https://api.groq.com/openai/v1`
6. Isi **Model ID** (misal `openai/gpt-oss-120b`).
7. Tes: kirim "hanya balas OK".

---

## Skenario 2: Proxy Lokal (AgentRouter) — TERUJI BERHASIL

### Mengapa butuh proxy?

Copilot mengirim request format OpenAI dengan header miliknya sendiri. AgentRouter (model Claude) menolak itu karena 4 hal yang **tidak bisa diperbaiki dari sisi VS Code**:

| # | Masalah | Akibat tanpa proxy | Yang proxy lakukan |
|---|---|---|---|
| 1 | Copilot tidak bisa kirim fingerprint header (`user-agent: claude-cli/...`) | `401 unauthorized client` | Proxy menyuntikkan fingerprint + header Anthropic |
| 2 | Copilot menyisipkan system prompt raksasa (~150-200KB) | `content-blocked` + boros kuota | Proxy menggantinya prompt ringkas |
| 3 | Copilot menyuntikkan blok XML konteks workspace (kadang bermuatan pola API key) | trigger moderasi | Proxy membersihkan tag XML + sensor pola key |
| 4 | Copilot pakai format OpenAI (`tool_calls`, `role: tool`), Claude butuh Anthropic (`tool_use`, `tool_result`) | error format | Proxy konversi dua arah + merge pesan + potong pesan >8000 char + retry content-blocked |

### Alur

```
VS Code Copilot
  → http://localhost:5099/v1/chat/completions   (format OpenAI)
       [proxy: konversi + fingerprint + anchor + sanitasi + retry]
  → https://agentrouter.org/v1/messages          (format Anthropic)
```

### Langkah

```bash
# 1. Install flask (sekali saja)
pip install flask

# 2. Jalankan proxy (biarkan terminal tetap terbuka)
python tools/proxy_openai_to_anthropic.py
# opsi: --port 8080 | --anchor coding (default) / general / extraction / text2sql / eval
```

Lalu di VS Code, ada **2 cara** mendaftarkan model:

#### Cara A: Lewat UI (satu per satu)

1. Copilot Chat → **Manage Models** → **Add Model** → **Custom Endpoint**.
2. Group name: `AgentRouter (Proxy)`, API Key: isi apa saja (key asli dibaca proxy dari `.env`).
3. API format: **OpenAI Chat Completions**.
4. Base URL: `http://localhost:5099/v1`
5. Model ID: `claude-opus-5`, `claude-opus-4-8`, atau `gpt-5.6-sol`.
6. Tes: kirim "hanya balas OK".

#### Cara B: Edit `chatLanguageModels.json` langsung (semua model sekaligus)

File lokasi: `%APPDATA%\Code\User\chatLanguageModels.json` (Windows) atau `~/.config/Code/User/chatLanguageModels.json` (Linux). Tambahkan entri berikut ke array terluar:

```json
{
  "name": "AgentRouter (Proxy)",
  "vendor": "customendpoint",
  "apiKey": "dummy-key-tidak-dipakai",
  "apiType": "chat-completions",
  "models": [
    {
      "id": "claude-opus-5",
      "name": "AR claude-opus-5",
      "url": "http://localhost:5099",
      "toolCalling": true,
      "vision": false,
      "maxInputTokens": 256000,
      "maxOutputTokens": 16000
    },
    {
      "id": "claude-opus-4-8",
      "name": "AR Claude Opus 4.8",
      "url": "http://localhost:5099",
      "toolCalling": true,
      "vision": true,
      "maxInputTokens": 200000,
      "maxOutputTokens": 4096
    },
    {
      "id": "gpt-5.6-sol",
      "name": "AR GPT-5.6 Sol",
      "url": "http://localhost:5099",
      "toolCalling": true,
      "vision": false,
      "maxInputTokens": 128000,
      "maxOutputTokens": 16000
    }
  ]
}
```

> **Catatan field penting:**
> - `apiKey`: isi string apa saja — proxy membaca key asli dari `.env`, bukan dari sini.
> - `url`: `http://localhost:5099` (tanpa `/v1` — Copilot menambahkan path sendiri).
> - `toolCalling: true`: wajib agar mode agent Copilot (baca file, jalankan command) berfungsi.
> - `maxOutputTokens`: jangan terlalu kecil — Claude butuh ruang untuk blok `thinking` sebelum menghasilkan teks (lihat gotcha di bawah).
> - Setelah edit, **restart VS Code** agar konfigurasi terbaca.

### Catatan operasional

- Proxy membaca config dari `providers/agentrouter.yaml` dan key dari `.env` — jadi key tidak pernah masuk konfigurasi VS Code.
- Log proxy: `tools/proxy.log` (berguna untuk debug content-blocked).
- Jika kena `content-blocked`, proxy otomatis retry dengan membuang riwayat tertua (hingga 12 kali).
- Mode agent Copilot (baca file, jalankan command) tetap berfungsi karena proxy meneruskan definisi tools dua arah.
- **Gotcha `maxOutputTokens`**: Claude Opus menghasilkan blok `thinking` (reasoning internal) sebelum teks jawaban. Jika `maxOutputTokens` terlalu kecil, semua token habis untuk thinking dan jawaban terlihat kosong (`content: null`). Set minimal 4096 (sudah dipakai di contoh di atas).

> ⚠️ **Keamanan proxy**: proxy berjalan di `localhost` **tanpa autentikasi**. Jangan expose port ini ke jaringan publik (mis. jangan `0.0.0.0` atau port-forward) karena proxy membawa API key dari `.env` dan meneruskan request ke upstream berbayar. Gunakan hanya di mesin lokal.
