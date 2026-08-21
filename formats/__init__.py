"""[FRAMEWORK] Registry format API.

Tambah format baru di sini (misal openai_responses, gemini), lalu daftarkan
di FORMAT_CLIENTS agar bisa dipakai lewat run.py.
"""

from . import anthropic_messages, openai_chat

FORMAT_CLIENTS = {
    "openai_chat": openai_chat,
    "anthropic_messages": anthropic_messages,
}
