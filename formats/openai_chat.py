"""[FRAMEWORK] Client format OpenAI Chat Completions.

Endpoint: POST {base_url}/chat/completions
Response: choices[0].message.content, usage.prompt_tokens/completion_tokens/total_tokens

Cuma butuh 1 provider? Lihat providers/<nama>/README.md (lebih sederhana).
"""

import time

import requests

from .base import (
    ANCHOR_ACK,
    build_headers,
    get_anchor,
    get_api_key,
)


def chat(cfg, model, prompt, max_tokens=512, timeout=120):
    """Kirim chat request. Return dict: {answer, usage, latency_ms, status}."""
    api_key = get_api_key(cfg)
    if not api_key:
        raise RuntimeError(f"API key tidak ditemukan untuk env var: {cfg.get('key_env')}")

    headers = build_headers(cfg, api_key)

    # Anchor hanya dipakai kalau provider mendeklarasikan moderation
    anchor = get_anchor(cfg)
    if anchor:
        messages = [
            {"role": "user", "content": anchor},
            {"role": "assistant", "content": ANCHOR_ACK},
            {"role": "user", "content": prompt},
        ]
    else:
        messages = [{"role": "user", "content": prompt}]

    url = cfg["base_url"].rstrip("/") + cfg.get("endpoint", "/chat/completions")

    start = time.time()
    resp = requests.post(
        url,
        headers=headers,
        json={"model": model, "max_tokens": max_tokens, "messages": messages},
        timeout=timeout,
    )
    latency_ms = (time.time() - start) * 1000

    if resp.status_code != 200:
        return {
            "answer": None,
            "status": resp.status_code,
            "error": resp.text[:300],
            "latency_ms": latency_ms,
        }

    data = resp.json()
    return {
        "answer": data["choices"][0]["message"]["content"],
        "usage": data.get("usage"),
        "status": resp.status_code,
        "latency_ms": latency_ms,
    }
