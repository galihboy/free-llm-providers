# Panduan Anchor (`anchors/`)

Anchor adalah **system prompt bahasa Inggris** yang di-prepend ke percakapan.
Fungsinya ada dua:

1. **Wajib** — membuat konteks dominan bahasa Inggris agar lolos moderasi
   provider tertentu (misal AgentRouter: prompt non-Inggris kena `content-blocked`).
2. **Sampingan** — mengarahkan persona/tugas model (coding, ekstraksi, chat bebas, dll).

Anchor hanya aktif untuk provider yang mendeklarasikan `moderation` di YAML-nya
(saat ini: AgentRouter). Provider lain (Groq, dll) mengabaikannya.

## Isi folder

| File | Kapan dipakai |
|---|---|
| `general.yaml` | Tugas umum netral (default saat `english_anchor: true`) |
| `coding.yaml` | Coding / software engineering — **cocok untuk VS Code Copilot via proxy** |
| `extraction.yaml` | Ekstraksi informasi dari teks (JSON/tabel/fields) |
| `text2sql.yaml` | Konversi bahasa alami → SQL |
| `eval.yaml` | Evaluasi/penilaian konten berdasarkan rubrik |
| `custom_chat.yaml` | Chat bebas santai multibahasa (contoh anchor kustom) |

## Cara pakai

### 1. Lewat CLI (override sementara, tanpa edit file)

```bash
# Lihat semua anchor yang tersedia
python run.py --list-anchors

# Pakai anchor bawaan
python run.py --provider agentrouter -m gpt-5.6-sol --anchor coding -p "jelaskan decorator Python"

# Pakai anchor dari file anchors/custom_chat.yaml
python run.py --provider agentrouter -m gpt-5.6-sol --anchor custom_chat -p "halo, apa kabar?"
```

### 2. Lewat YAML provider (permanen untuk provider tersebut)

Di `providers/<nama>.yaml`, bagian `moderation` (prioritas dari tinggi ke rendah):

```yaml
moderation:
  # Opsi A: teks bebas — override penuh, menang atas semua
  anchor_text: "You are a pirate. Answer in English."

  # Opsi B: file anchor di folder anchors/
  anchor_file: custom_chat

  # Opsi C: varian bawaan ATAU nama file anchors/*.yaml
  english_anchor: coding      # atau: true (= general)
```

> Catatan: kalau `anchor_text` dan `anchor_file`/`english_anchor` diisi
> sekaligus, `anchor_text` yang menang.

### 3. Untuk VS Code Copilot (via proxy)

Proxy `tools/proxy_openai_to_anthropic.py` default memakai anchor **coding**
karena memang untuk skenario coding di editor. Ganti anchor tanpa edit kode:

```bash
python tools/proxy_openai_to_anthropic.py --anchor vscode_coding   # file lokal provider
python tools/proxy_openai_to_anthropic.py --anchor custom_chat     # file global
```

## Membuat anchor baru

1. Salin file mana pun, misal `custom_chat.yaml`, beri nama baru
   (huruf kecil, underscore, tanpa spasi): `anchors/terjemahan.yaml`
2. Isi minimal 2 field:

```yaml
name: terjemahan
description: Penerjemah profesional multibahasa
prompt: >-
  You are a professional translator. Translate the user's text accurately
  into the target language they request, preserving tone and formatting.
  Do not add commentary unless asked.
```

3. Langsung bisa dipakai tanpa edit kode Python apa pun:

```bash
python run.py --provider agentrouter -m gpt-5.6-sol --anchor terjemahan -p "terjemahkan ke Jepang: selamat pagi"
```

## Anchor lokal per-provider (`providers/<nama>/anchors/`)

Selain folder global `anchors/`, tiap provider boleh punya folder anchor
sendiri di `providers/<nama>/anchors/`. Aturan pencarian:

1. **`providers/<nama>/anchors/<nama>.yaml`** — lokal provider, **menang**
2. **`anchors/<nama>.yaml`** — global, fallback

Gunakan anchor lokal kalau anchor itu **spesifik untuk satu provider**
(misal persona khusus AgentRouter). Gunakan global kalau anchor generik
dan bisa dipakai provider mana pun.

Contoh yang sudah ada: `providers/agentrouter/anchors/vscode_coding.yaml`
(persona coding ringkas untuk skenario VS Code Copilot via proxy).

```bash
# Lihat anchor global + lokal provider
python run.py --list-anchors --provider agentrouter

# Pakai anchor lokal provider
python run.py --provider agentrouter -m gpt-5.6-sol --anchor vscode_coding -p "jelaskan decorator"

# Proxy juga mendukung file lokal provider
python tools/proxy_openai_to_anthropic.py --anchor vscode_coding
```

> Kalau nama file lokal sama dengan global, yang lokal dipakai dan yang
> global diabaikan (tanpa error).

## Tips

- **Prompt anchor harus bahasa Inggris** — ini inti fungsinya (lolos moderasi).
  Bahasa jawaban tetap mengikuti bahasa user (sudah disebut di tiap anchor).
- Satu file = satu tugas. Jangan gabungkan banyak persona dalam satu anchor.
- Registry bawaan di `formats/base.py` (`ANCHORS`) tetap ada sebagai fallback;
  file YAML di folder ini lebih disarankan karena bisa ditambah tanpa edit kode.
