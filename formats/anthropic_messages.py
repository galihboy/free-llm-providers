"""[FRAMEWORK] Client format Anthropic Messages.

Endpoint: POST {base_url}/messages  (perhatikan: base_url TANPA /v1 untuk AgentRouter)
Response: content[] (type text/thinking), usage.input_tokens/output_tokens

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


def chat(cfg, model, prompt, max_tokens=1024, timeout=120):
    """Kirim chat request format Anthropic. Return dict: {answer, usage, latency_ms, status}."""
    api_key = get_api_key(cfg)
    if not api_key:
        raise RuntimeError(f"API key tidak ditemukan untuk env var: {cfg.get('key_env')}")

    headers = build_headers(cfg, api_key)
    # Header wajib format Anthropic
    headers.setdefault("anthropic-version", "2023-06-01")

    # Anchor hanya dipakai kalau provider mendeklarasikan moderation
    anchor = get_anchor(cfg)
    if anchor:
        messages = [
            {"role": "user", "content": [{"type": "text", "text": anchor}]},
            {"role": "assistant", "content": [{"type": "text", "text": ANCHOR_ACK}]},
            {"role": "user", "content": prompt},
        ]
    else:
        messages = [{"role": "user", "content": prompt}]

    url = cfg["base_url"].rstrip("/") + cfg.get("endpoint", "/v1/messages")

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

    # Parse content[] — bisa berisi blok text dan/atau thinking
    texts = []
    for c in data.get("content", []):
        if isinstance(c, dict):
            if c.get("type") == "text":
                texts.append(c.get("text", ""))
            elif c.get("type") == "thinking":
                texts.append(c.get("thinking", c.get("text", "")))
    answer = "".join(texts) if texts else None

    return {
        "answer": answer,
        "usage": data.get("usage"),
        "status": resp.status_code,
        "latency_ms": latency_ms,
    }
