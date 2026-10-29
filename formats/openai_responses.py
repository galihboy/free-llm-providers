"""[FRAMEWORK] Client OpenAI Responses API."""

import time

import requests

from .base import ANCHOR_ACK, build_headers, get_anchor, get_api_key


def chat(cfg, model, prompt, max_tokens=512, timeout=120):
    """Kirim request Responses. Return dict serupa client chat lainnya."""
    api_key = get_api_key(cfg)
    if not api_key:
        raise RuntimeError(f"API key tidak ditemukan untuk env var: {cfg.get('key_env')}")

    headers = build_headers(cfg, api_key)
    anchor = get_anchor(cfg)
    input_items = []
    if anchor:
        input_items.extend(
            [
                {"role": "user", "content": [{"type": "input_text", "text": anchor}]},
                {"role": "assistant", "content": [{"type": "output_text", "text": ANCHOR_ACK}]},
            ]
        )
    input_items.append({"role": "user", "content": [{"type": "input_text", "text": prompt}]})

    url = cfg["base_url"].rstrip("/") + cfg.get("endpoint", "/responses")
    start = time.time()
    resp = requests.post(
        url,
        headers=headers,
        json={"model": model, "max_output_tokens": max_tokens, "input": input_items},
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

    try:
        data = resp.json()
    except ValueError:
        return {
            "answer": None,
            "status": resp.status_code,
            "error": "respons bukan JSON yang valid",
            "latency_ms": latency_ms,
        }
    answer = data.get("output_text")
    if not answer:
        texts = []
        for item in data.get("output", []):
            if not isinstance(item, dict):
                continue
            for content in item.get("content", []):
                if isinstance(content, dict) and content.get("type") == "output_text":
                    texts.append(content.get("text", ""))
        answer = "".join(texts) or None
    return {
        "answer": answer,
        "usage": data.get("usage"),
        "status": resp.status_code,
        "latency_ms": latency_ms,
    }
