# Integrasi ke Tools Coding

Panduan umum memasang provider LLM gratis ke tools coding. Untuk konfigurasi spesifik per provider, lihat juga `providers/<nama>/integrasi.md`.

## Prinsip Utama: Cocokkan Format API

Setiap tool coding mendukung format API tertentu. Cocokkan dengan format yang disediakan provider:

| Tool Coding | Format Didukung | Catatan |
|---|---|---|
| VS Code GitHub Copilot | Anthropic Messages + OpenAI Chat | via "Add Model → Custom Endpoint" |
| OpenCode | Anthropic + OpenAI-compatible | via `opencode.json` |
| Claude Code | Anthropic Messages | via env `ANTHROPIC_*`, base URL tanpa `/v1` |
| Codex | OpenAI Responses | via `~/.codex/config.toml`, `wire_api="responses"` |
| Cursor | OpenAI Chat | via Override Base URL `.../v1` |
| Cline / Roo Code / Kilo Code | Anthropic + OpenAI | via settings provider |

## Aturan Base URL

- Format **Anthropic** → base URL biasanya **tanpa** `/v1` (tool menambahkan path `/v1/messages` sendiri)
- Format **OpenAI** → base URL **dengan** `/v1` (endpoint `/chat/completions` ditambahkan tool)
- **Jangan dicampur** — ini penyebab error paling umum.

## Gotcha Umum

1. **Fingerprint client**: beberapa provider (misal AgentRouter) memverifikasi identitas client lewat header. Jika dapat `401 unauthorized client` padahal key benar, cek dokumentasi provider untuk header wajib.
2. **Moderasi bahasa**: beberapa provider memblokir prompt non-Inggris. Solusi: anchor bahasa Inggris di awal percakapan (lihat `formats/base.py`).
3. **Model spesifik per key**: satu provider bisa menerbitkan key dengan hak model berbeda. Cek `--list-models`.

## Panduan per Tool

- [VS Code GitHub Copilot](vscode-copilot.md)
- [OpenCode](opencode.md)
- [Claude Code](claude-code.md)
- [Codex](codex.md)
