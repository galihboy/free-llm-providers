# HCNSec 🆓

> 🔄 Standalone script: sinkron dengan `formats/` per 2026-09-23
> ℹ️ Provider ini juga tersedia via framework: `python run.py --provider hcnsec`

**HCNSec** (https://api.hcnsec.cn/) — gateway agregator LLM **公益 (public-welfare)** dari 新疆幻城网安科技有限责任公司 (Xinjiang Huancheng Cybersecurity), dibangun di atas **NewAPI**. Bukan model sendiri: murni relay ke upstream. Klaim free credit saat registrasi + harian check-in; OpenAI-compatible penuh.

## Info Dasar

| | |
|---|---|
| Website / Daftar | https://api.hcnsec.cn/sign-up?aff=Q7jj |
| Ambil API key | Console → 密钥/token → buat token `sk-...` (group `auto`) |
| Kuota gratis | Free credit registrasi + check-in harian (sistem kredit, bukan unlimited) |
| Docs | https://api.hcnsec.cn/free-api/ |
| Model list (docs) | https://api.hcnsec.cn/free-api/models/ |
| Cek kuota | `GET /api/usage/token` (header Bearer) |

> ⚠️ **Risiko relay**: probe pihak ketiga (BazaarLink) melaporkan banyak model free **substitution** (identitas upstream tidak sesuai label). Sustainability "gratis selamanya" diragukan. **Oke utk eksperimen, jangan utk data sensitif/produksi.** Repurtasi independen: freeairouter 55/100 (risk Medium).

> 💡 **Referral disclosure**: tautan pendaftaran HCNSec di dokumen ini adalah link afiliasi (referral). Mau netral? Pakai https://api.hcnsec.cn/sign-up tanpa parameter `aff`.

## Model Tersedia

### Teruji lolos (2026-09-23) — dipakai sebagai default YAML

| Model | Catatan |
|---|---|
| `DeepSeek-V4-Flash` | ✅ default; reasoning (pakai `-t ≥1024`) |
| `glm-5.3-flash` | ✅ lightweight GLM free layer |
| `Qwen3.8-27B` | ✅ open-weight 27B |
| `Qwen3.8-Flash-Next` | ✅ flash |
| `sensenova-6.8-flash-lite` | ✅ juga tersedia langsung di SenseNova resmi |

### Terdaftar live tapi GAGAL tes (2026-09-23)

| Model | Err |
|---|---|
| `MiniMax-M3`, `step-3.7-flash`, `step-router-v1` | `500 get_channel_failed` — listed, channel group auto tidak ada |
| `DeepSeek-V4-Pro` | `404 openai_error` |
| `DeepSeek-V4.1-Flash` | `400 not supported` |
| `kimi-k3` | timeout >120s (2× percobaan) |
| `auto` | `522` |

Full live list (28 model, termasuk tier svip & audio/image): `python run.py --provider hcnsec --list-models`.

> ⚠️ Nama model **CASE-SENSITIVE** — pakai string persis dari `--list-models`, bukan lowercase vendor resmi.
> ⚠️ **Rate limit ketat**: `400 Throttling.RateQuota` muncul jika tes beruntun — window bisa >90s; beri jeda antar request.

Tier **SVIP** (butuh langganan ¥19,9+/mgg, token auto-upgrade): `glm-5.3`, `qwen3.7-plus`, `MiniMax-M2.7`, Spark X2, `mimo-v2.5`, dll — muncul di `/v1/models` tapi aksesnya beda group.

## Dua Endpoint

| Format | Base URL | Endpoint |
|---|---|---|
| OpenAI Chat Completions | `https://api.hcnsec.cn/v1` | `/chat/completions` |
| Anthropic (diklaim utk Claude Code) | `https://api.hcnsec.cn` (tanpa `/v1`) | `/v1/messages` — **belum teruji di repo ini** |

## Cara Pakai (Standalone)

```bash
# 1. Isi .env di folder ini (atau root repo)
HCNSEC_API_KEY=sk-xxxxx

# 2. Chat (default model: DeepSeek-V4-Flash)
python chat.py -m DeepSeek-V4-Flash -p "jelaskan LLM dalam 1 kalimat"

# 3. Smart routing
python chat.py -m auto -p "halo"

# 4. List model (live — daftar bisa berubah)
python chat.py --list-models
```

## Cara Pakai (Framework)

```bash
# dari root repo
python run.py --provider hcnsec -m DeepSeek-V4-Flash -p "say OK"
python run.py --provider hcnsec --list-models
```

## ⚠️ Gotcha (WAJIB BACA)

1. **Case-sensitive**: `DeepSeek-V4-Flash` ✅ · `deepseek-v4-flash` ❌. Selalu cek `--list-models`.
2. **Rate limit ketat**: `400 Throttling.RateQuota` kalau tes beruntun — window bisa >90s; jeda beberapa detik antar request.
3. **Channel tidak selalu ada**: model muncul di `/v1/models` tapi bisa `500 get_channel_failed` (group auto) — daftar ≠ siap pakai.
4. **Token group**: token group **`auto`**. Salah group → `403` / "kuota ada tapi model tidak tercapai".
5. **Tier free vs svip**: `glm-5.3-flash` free; `glm-5.3` (tanpa `-flash`) = svip.
6. **Arti error**: `401` key salah · `403` group/scope · `400 Throttling` rate limit · `500 get_channel_failed` no channel · `503/522` upstream down · format `new_api_error`.
7. **Model reasoning**: `max_tokens` kecil → jawaban kosong; pakai `-t ≥1024`.
8. **Identitas model tidak terjamin**: relay agregator; probe BazaarLink laporkan substitution.
9. **Privasi**: konten melewati relay pihak ketiga. Jangan kirim data sensitif.
10. **Kuota dinamis**: tutorial lama "unlimited" → kini sistem kredit. Cek `/api/usage/token`.
11. **IPv6 hang** (Windows): script standalone force IPv4 (pola sama `formats/base.py`).

## Status Pengujian (2026-09-23)

- ✅ `run.py --list-models` [LIVE]: 28 model
- ✅ Framework `run.py`: `DeepSeek-V4-Flash` (31s cold / 5s warm), `glm-5.3-flash` (3.6s), `Qwen3.8-27B` (14s), `Qwen3.8-Flash-Next` (13s), `sensenova-6.8-flash-lite` (4.3s)
- ✅ Standalone `chat.py`: `DeepSeek-V4-Flash` 200 OK (5.4s)
- ❌ `MiniMax-M3`/`step-3.7-flash`/`step-router-v1`: 500 no channel · `DeepSeek-V4-Pro`: 404 · `kimi-k3`: timeout · `auto`: 522
- ⚠️ `smoke_test_all.py`: kena rate limit (`400 Throttling`) kalau dijalankan beruntun setelah tes manual — **LOLOS** setelah cooldown 60s (`DeepSeek-V4-Flash` 32.6s); rate limit window bisa >90s, jangan spam tes.

## Integrasi Tools Coding

Provider standar OpenAI-compatible → bisa dipasang langsung ke Cursor / Cline / Copilot custom endpoint
(Base URL `https://api.hcnsec.cn/v1`, **tanpa proxy** — tidak ada fingerprint). Panduan umum: [integrations/](../../integrations/README.md).

## Referensi

- [Dokumentasi free API](https://api.hcnsec.cn/free-api/)
- [Model list](https://api.hcnsec.cn/free-api/models/)
- [Blog tutorial resmi (幻城笔记)](https://hcnote.cn/)
- Probe independen: [BazaarLink](https://bazaarlink.ai/en/probe/relay/api.hcnsec.cn) · [freeairouter](https://freeairouter.com/s/api.hcnsec.cn)
