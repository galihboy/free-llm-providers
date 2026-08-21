# Panduan Kontribusi

Terima kasih sudah mau berkontribusi! Repo ini punya **dua lapisan** yang harus dijaga sinkron:

1. **Script standalone** (`providers/<nama>/*.py`) — untuk pengguna yang cuma butuh 1 provider, bisa copy & jalan.
2. **Framework terintegrasi** (`formats/` + `providers/*.yaml` + `run.py`) — untuk kelola banyak provider.

## Aturan Sinkronisasi (WAJIB)

| Jenis perubahan | Edit di | Lalu |
|---|---|---|
| Data provider (model, kuota, gotcha, endpoint) | **HANYA** `providers/<nama>.yaml` + `data/providers.json` | Update README provider jika perlu |
| Logika format API (header, payload, parsing) | **HANYA** `formats/<format>.py` | Sync ke script standalone provider terkait |
| Provider baru | Buat `providers/<nama>.yaml` + folder `providers/<nama>/` (README + script standalone) | Tambah baris di README root + `data/providers.json` |

## Menambah Provider Baru

1. Buat `providers/<nama>.yaml` — isi hanya field yang **memang dibutuhkan**:
   - `extra_headers` → hanya kalau provider butuh header khusus
   - `moderation.english_anchor` → hanya kalau ada moderasi bahasa
   - `list_models` → hanya kalau endpoint `/models` tersedia (kalau tidak, cukup andalkan `models:` statis)
2. Buat folder `providers/<nama>/`:
   - `README.md` — info lengkap standalone (kuota, model, cara pakai, gotcha)
   - Script standalone (copy dari provider sejenis, sesuaikan)
   - `integrasi.md` (opsional) — jika ada cara pasang ke tools coding
3. Tambahkan ke tabel di `README.md` root dan `data/providers.json`.
4. Tes: `python run.py --provider <nama> -p "say OK"` dan script standalone-nya.

## Menambah Format API Baru

1. Buat `formats/<format_baru>.py` dengan fungsi `chat(cfg, model, prompt, max_tokens, timeout)` yang return `{answer, usage, status, latency_ms}`.
2. Daftarkan di `formats/__init__.py` → `FORMAT_CLIENTS`.
3. Pakai di YAML provider: `formats: { <format_baru>: {...} }`.

## Keamanan

- **JANGAN** commit file `.env` atau API key asli.
- Contoh key di dokumentasi harus dummy (`sk-xxxxx`).
- Jika tidak sengaja commit key: rotate segera + hapus dari history (`git filter-repo`).

## Penanda Status

Di README provider, cantumkan badge sinkronisasi:

```markdown
> 🔄 Standalone script: sinkron dengan formats/ per YYYY-MM-DD
```

Jika standalone belum di-sync setelah perubahan framework, ganti jadi:

```markdown
> ⚠️ Standalone script belum di-sync dengan formats/ (terakhir: YYYY-MM-DD)
```
