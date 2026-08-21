# Groq 🆓

> 🔄 Standalone script: sinkron dengan `formats/` per 2026-08-20
> ℹ️ Provider ini juga tersedia via framework: `python run.py --provider groq`

**Groq** (https://console.groq.com) terkenal dengan inferensi **sangat cepat** (LPU). Free tier tersedia dengan rate limit harian. Contoh provider **standar**: tanpa extra header, tanpa anchor bahasa.

## Info Dasar

| | |
|---|---|
| Website | https://console.groq.com |
| Ambil API key | https://console.groq.com/keys |
| Kuota gratis | free tier, rate limit harian |
| Format API | OpenAI Compatible |

## Model Populer (per 2026-08-20)

| Model | ID |
|---|---|
| GPT-OSS 120B | `openai/gpt-oss-120b` |
| GPT-OSS 20B | `openai/gpt-oss-20b` |
| Qwen 3.6 27B | `qwen/qwen3.6-27b` |
| Compound Mini | `groq/compound-mini` |

> ⚠️ Daftar model Groq sering berubah (model lama seperti `llama-3.3-70b-versatile` sudah tidak ada). Selalu cek `--list-models` untuk daftar terkini.

## Cara Pakai (Standalone)

```bash
# 1. Isi .env
GROQ_API_KEY=gsk_xxxxx

# 2. Chat
python chat.py -m openai/gpt-oss-120b -p "jelaskan LLM dalam 1 kalimat"

# 3. List model
python chat.py --list-models
```

## Gotcha

- Rate limit harian free tier — kalau kena 429, tunggu atau kurangi frekuensi.
- Daftar model bisa berubah sewaktu-waktu; cek `--list-models` untuk yang terkini.
