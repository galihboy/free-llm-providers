"""[FRAMEWORK] Registry format API.

Tambah format baru di sini (misal gemini), lalu daftarkan
di FORMAT_CLIENTS agar bisa dipakai lewat run.py.
"""

from . import (
    anthropic_messages,
    openai_chat,
    openai_images,
    openai_images_edits,
    openai_responses,
)

FORMAT_CLIENTS = {
    "openai_chat": openai_chat,
    "openai_responses": openai_responses,
    "anthropic_messages": anthropic_messages,
    "openai_images": openai_images,
    "openai_images_edits": openai_images_edits,
}
