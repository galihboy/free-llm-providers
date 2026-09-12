# SenseNova 🆓

> 🔄 Standalone script: sinkron dengan `formats/` per 2026-09-09
> ℹ️ Provider ini juga tersedia melalui framework: `python run.py --provider sensenova`

**SenseNova** (https://www.sensenova.ai) adalah layanan API dari SenseTime dengan
endpoint yang kompatibel dengan OpenAI dan Anthropic. Model tersedia gratis selama
public beta, dengan kuota dan sistem poin yang dapat berubah.

## Info Dasar

| | |
|---|---|
| Website | https://www.sensenova.ai |
| Ambil API key | https://platform.sensenova.ai/console/keys |
| Variabel API key | `SENSENOVA_API_KEY` |
| Kuota gratis | 1.500 panggilan / 5 jam per model selama public beta |
| Format API | OpenAI Compatible dan Anthropic Compatible |
| Dokumentasi | https://platform.sensenova.ai/docs |

## Model Populer (per 2026-09-09)

| Model | ID | Tipe | Input | Output | Catatan |
|---|---|---|---|---|---|
| SenseNova 6.8 Flash Lite | `sensenova-6.8-flash-lite` | chat multimodal | teks, gambar | teks | model utama; tool calling, reasoning, streaming |
| SenseNova 6.7 Flash Lite | `sensenova-6.7-flash-lite` | chat multimodal | teks, gambar | teks | kompatibilitas diarahkan ke 6.8 |
| SenseNova U1.5 Lite | `sensenova-u1.5-lite` | generasi dan edit gambar | teks, gambar referensi | gambar | text-to-image dan image-to-image |
| SenseNova U1 Fast | `sensenova-u1-fast` | generasi infografis | teks | gambar | khusus endpoint image generation |

> ⚠️ `sensenova-u1-fast` bukan model chat dan tidak mendukung input gambar.

## Cara Pakai (Framework)

Isi `.env` di root repositori:

```dotenv
SENSENOVA_API_KEY=sk-xxxxx
```

Atau set environment variable di PowerShell:

```powershell
$env:SENSENOVA_API_KEY="sk-xxxxx"
```

### Chat OpenAI

```bash
python run.py --provider sensenova --format openai_chat \
  -m sensenova-6.8-flash-lite -p "jelaskan LLM dalam satu kalimat"
```

### Chat Anthropic

```bash
python run.py --provider sensenova --format anthropic_messages \
  -m sensenova-6.8-flash-lite -p "jelaskan LLM dalam satu kalimat"
```

### Membuat Gambar

```bash
python run.py --provider sensenova --format openai_images \
  -m sensenova-u1.5-lite -p "seekor kucing merah muda yang lucu"
```

Untuk membuat infografis:

```bash
python run.py --provider sensenova --format openai_images \
  -m sensenova-u1-fast -p "infografis tentang prinsip kecerdasan buatan"
```

Perintah `run.py` menampilkan hasil Base64 atau URL, tetapi belum menyimpan hasil
gambar ke file secara otomatis.

### Daftar Model

```bash
python run.py --provider sensenova --list-models
```

## Cara Pakai (Standalone)

```bash
cd providers/sensenova

# Chat OpenAI
python chat.py -m sensenova-6.8-flash-lite -p "jelaskan LLM dalam satu kalimat"

# Chat Anthropic
python chat.py --api anthropic -p "jelaskan LLM dalam satu kalimat"

# Daftar model
python chat.py --list-models

# Membuat gambar; hasil disimpan ke folder saat ini
python image.py generate -p "seekor kucing merah muda yang lucu"

# Membuat infografis
python image.py generate -m sensenova-u1-fast -s 2752x1536 \
  -p "infografis tentang prinsip kecerdasan buatan"

# Edit gambar dari file lokal atau URL publik
python image.py edit -i sumber.png -p "ubah latar belakang menjadi pegunungan"
```

Script standalone membaca `SENSENOVA_API_KEY` dari environment atau `.env` di
root repositori. `image.py` menyimpan hasil Base64 ke file dan mendukung
`--no-watermark` serta `--no-prompt-extend`.

## Format API

### OpenAI Chat Completions (`openai_chat`)

- Base URL: `https://token.sensenova.ai/v1`
- Endpoint: `/chat/completions`
- Mendukung input gambar, tool calling, reasoning, dan streaming SSE.

### Anthropic Messages (`anthropic_messages`)

- Base URL: `https://token.sensenova.ai` tanpa `/v1`.
- Endpoint: `/v1/messages`.
- Mendukung input gambar melalui URL atau Base64, tool calling, dan streaming SSE.

### Generasi Gambar (`openai_images`)

- Base URL: `https://token.sensenova.ai/v1`.
- Endpoint: `/images/generations`.
- Model: `sensenova-u1.5-lite` dan `sensenova-u1-fast`.
- Format hasil: `b64_json` atau URL sementara.

### Edit Gambar (`openai_images_edits`)

- Base URL: `https://token.sensenova.ai/v1`.
- Endpoint: `/images/edits`.
- Model: `sensenova-u1.5-lite`.
- Input gambar berupa URL publik atau Data URL Base64.
- CLI `run.py` belum menyediakan argumen untuk memasukkan gambar; gunakan
  `image.py edit` atau fungsi `formats.openai_images_edits.edit()`.

## Parameter Penting

### Chat

```json
{
  "model": "sensenova-6.8-flash-lite",
  "messages": [],
  "temperature": 0.6,
  "top_p": 0.95,
  "max_tokens": 65535,
  "reasoning_effort": "medium",
  "stream": false,
  "tools": [],
  "tool_choice": "auto"
}
```

`reasoning_effort` menerima `low`, `medium`, `high`, atau `none`.

### Generasi Gambar

```json
{
  "model": "sensenova-u1.5-lite",
  "prompt": "seekor berang-berang laut mengapung di laut yang tenang",
  "n": 1,
  "size": "1024x1024",
  "output_format": "png",
  "response_format": "b64_json",
  "watermark": true,
  "prompt_extend": true
}
```

`n` saat ini hanya mendukung nilai `1`. Ukuran harus memiliki sisi minimum 512
dan dimensi kelipatan 32.

### Edit Gambar

```json
{
  "model": "sensenova-u1.5-lite",
  "images": [{"image_url": "https://example.com/source.png"}],
  "prompt": "ubah latar belakang menjadi pegunungan",
  "n": 1,
  "size": "auto",
  "watermark": true,
  "prompt_extend": true,
  "response_format": "b64_json"
}
```

URL sumber harus dapat diakses langsung oleh server SenseNova. Alternatifnya,
gunakan Data URL dengan format `data:image/png;base64,...`.

## Sistem Poin

- **General Points**: dapat digunakan untuk model yang termasuk Token Plan.
- **Flash-Lite Points**: digunakan lebih dahulu oleh model Flash Lite.
- Batas public beta: 60.000 poin / 5 jam dan 600.000 poin / 7 hari.
- Program rebate: setiap 1 Flash-Lite Point yang digunakan menghasilkan 1 General
  Point pada hari berikutnya; poin rebate berlaku selama 30 hari.

## Hasil Pengujian

- Chat OpenAI: ✅ berhasil dengan `sensenova-6.8-flash-lite`.
- Chat Anthropic: ✅ berhasil dengan `sensenova-6.8-flash-lite`.
- Generasi gambar melalui `run.py`: ✅ berhasil dengan `sensenova-u1.5-lite`.
- Chat standalone: ✅ berhasil melalui `chat.py`.
- Generasi gambar standalone: ✅ berhasil dan PNG tersimpan ke file.
- Edit gambar standalone: ✅ berhasil menggunakan PNG lokal hasil generation.
- CLI `run.py` belum menyediakan argumen untuk memasukkan gambar; gunakan
  `image.py edit` untuk alur edit standalone.
- `tools/smoke_test_all.py` hanya menguji format chat; format gambar perlu diuji
  melalui `run.py` atau fungsi image client secara langsung.

## Gotcha

1. OpenAI base URL harus menyertakan `/v1`: `https://token.sensenova.ai/v1`.
2. Anthropic base URL tidak boleh menyertakan `/v1`: `https://token.sensenova.ai`.
3. URL hasil gambar bersifat sementara: sekitar 24 jam untuk U1.5 Lite dan 1 jam
   untuk U1 Fast. Unduh hasil segera.
4. `response_format=b64_json` lebih praktis karena tidak membutuhkan permintaan
   unduhan kedua.
5. Selalu kirim `watermark` secara eksplisit karena fitur tanpa watermark gratis
   selama beta dan dapat menjadi fitur berbayar setelah beta.
6. Error `429` berarti kuota atau rate limit terlampaui; gunakan retry dengan
   exponential backoff.
7. Error `403` berarti akses model ditolak untuk key atau wilayah akun.
8. Error `404` biasanya berarti model tidak dikenal atau sudah dihentikan.
9. `sensenova-6.7-flash-lite` masih muncul di `/v1/models`, tetapi untuk konfigurasi
  baru gunakan `sensenova-6.8-flash-lite`.

## Referensi

- [Dokumentasi API](https://platform.sensenova.ai/docs)
- [Daftar model](https://www.sensenova.ai/models)
- [Token Plan](https://www.sensenova.ai/token-plan)
- [Console dan API key](https://platform.sensenova.ai/console)
- [SenseNova Skills](https://github.com/OpenSenseNova/SenseNova-Skills)