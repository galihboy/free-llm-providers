# Roadmap & Progress

Status perkembangan proyek dan rencana ke depan. Untuk riwayat perubahan detail lihat [CHANGELOG.md](CHANGELOG.md).

## Progress Provider

| Provider | YAML | Standalone | Teruji | Integrasi | Catatan |
|---|---|---|---|---|---|
| AgentRouter | ✅ | ✅ | ✅ 2026-08-20 | ✅ | 2 format (Anthropic + OpenAI) |
| Groq | ✅ | ✅ | ✅ 2026-08-20 | — | contoh provider standar |

### Kandidat Berikutnya (dari koleksi tes sebelumnya)

| Provider | Kuota | Prioritas | Status |
|---|---|---|---|
| BluesMinds | $100 credit | tinggi | belum dipindah |
| Naraya | 7jt token/hari | tinggi | belum dipindah |
| Cerebras | free tier | sedang | belum dipindah |
| SiliconFlow | 1 credit signup | sedang | belum dipindah |
| TokenRouter | credit | sedang | belum dipindah |
| Aero | free 2 minggu | sedang | belum dipindah |

> Kriteria masuk repo: gratis (atau free credit), teruji jalan, dan boleh dibagikan secara publik.

## Rencana Pengembangan

### Jangka Pendek
- [ ] Tambah 3-5 provider dari daftar kandidat
- [ ] Format `openai_responses` (untuk Codex `wire_api="responses"`)
- [ ] Badge status otomatis di README dari hasil `smoke_test_all.py`

### Jangka Menengah
- [ ] GitHub Actions: smoke test terjadwal (deteksi provider mati/model berganti otomatis)
- [ ] Generator README tabel provider dari `data/providers.json` (anti-drift)
- [ ] Template cookiecutter untuk menambah provider baru

### Ide (Belum Dijadwalkan)
- [ ] Perbandingan latency antar provider (benchmark)
- [ ] Halaman web sederhana untuk browse provider

## Cara Update Halaman Ini

- Pindahkan baris provider dari "Kandidat" ke "Progress" setelah YAML + standalone + tes selesai.
- Centang `[x]` item rencana yang sudah dikerjakan.
- Catat perubahan penting di [CHANGELOG.md](CHANGELOG.md), bukan di sini.
