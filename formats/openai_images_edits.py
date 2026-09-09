"""[FRAMEWORK] Client format OpenAI Images Edits.

Endpoint: POST {base_url}/images/edits
Response: data[].b64_json or data[].url

Cuma butuh 1 provider? Lihat providers/<nama>/README.md (lebih sederhana).
"""

import time

import requests

from .base import (
    build_headers,
    get_api_key,
)


def edit(cfg, model, prompt, images, n=1, size="auto", response_format="b64_json", timeout=120, **kwargs):
    """Kirim image edit request. Return dict: {images, usage, latency_ms, status}."""
    api_key = get_api_key(cfg)
    if not api_key:
        raise RuntimeError(f"API key tidak ditemukan untuk env var: {cfg.get('key_env')}")

    headers = build_headers(cfg, api_key)

    url = cfg["base_url"].rstrip("/") + cfg.get("endpoint", "/images/edits")

    payload = {
        "model": model,
        "prompt": prompt,
        "images": images,
        "n": n,
        "size": size,
        "response_format": response_format,
    }
    # Add extra params (watermark, prompt_extend, etc.)
    payload.update(kwargs)

    start = time.time()
    resp = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=timeout,
    )
    latency_ms = (time.time() - start) * 1000

    if resp.status_code != 200:
        return {
            "images": None,
            "status": resp.status_code,
            "error": resp.text[:300],
            "latency_ms": latency_ms,
        }

    data = resp.json()
    return {
        "images": data.get("data", []),
        "usage": data.get("usage"),
        "status": resp.status_code,
        "latency_ms": latency_ms,
    }