"""[STANDALONE] Chat HCNSec (幻城网安公益API) via OpenAI Compatible API.

Bisa jalan sendiri: cukup file ini + .env berisi HCNSEC_API_KEY.
Tidak butuh folder formats/ atau run.py.
Versi terintegrasi (multi-provider): lihat /run.py

Endpoint: POST https://api.hcnsec.cn/v1/chat/completions
Model teruji (2026-09-23): DeepSeek-V4-Flash, glm-5.3-flash,
          Qwen3.8-27B, Qwen3.8-Flash-Next, sensenova-6.8-flash-lite
Gagal: MiniMax-M3/step* (500 no channel), DeepSeek-V4-Pro (404), kimi-k3 (timeout)

GOTCHA:
  - Model name CASE-SENSITIVE (mis. DeepSeek-V4-Flash, bukan deepseek-v4-flash).
  - Rate limit ketat: 400 Throttling.RateQuota jika tes beruntun — jeda antar req.
  - Token group "auto" wajib; salah group -> 403 / model tidak tercapai.
  - Tier free vs svip: svip (glm-5.3, qwen3.7-plus, ...) butuh langganan.
  - Relay NewAPI: identitas model bisa substitution (risiko pihak ketiga).
  - 401 = key salah; 403 = group/scope; 400 Throttling = rate limit.

Contoh:
  python chat.py -m DeepSeek-V4-Flash -p "jelaskan LLM dalam 1 kalimat"
  python chat.py -m auto -p "halo"          # smart routing
  python chat.py --list-models
"""

import argparse
import os
import socket
import sys
import time

import requests

# Force IPv4 — beberapa koneksi ke api.hcnsec.cn hang di IPv6 (Windows).
_orig = socket.getaddrinfo
socket.getaddrinfo = lambda h, p, *a, **k: [
    r for r in _orig(h, p, *a, **k) if r[0] == socket.AF_INET
]

BASE_URL = "https://api.hcnsec.cn/v1"
KEY_ENV = "HCNSEC_API_KEY"


def get_api_key():
    key = os.getenv(KEY_ENV)
    if key:
        return key
    here = os.path.dirname(os.path.abspath(__file__))
    for env_path in (os.path.join(here, ".env"), os.path.join(here, "..", "..", ".env")):
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(f"{KEY_ENV}="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def list_models(api_key):
    r = requests.get(
        f"{BASE_URL}/models",
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=30,
    )
    if r.status_code != 200:
        print(f"HTTP {r.status_code}: {r.text[:200]}")
        sys.exit(1)
    print("Model tersedia:")
    for m in r.json().get("data", []):
        print(f"  - {m.get('id')}")


def chat(api_key, model, prompt, max_tokens=512):
    print(f"Base URL: {BASE_URL}")
    print(f"Model: {model}")
    print(f"Pesan: {prompt}")
    print("-" * 60)

    start = time.time()
    resp = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "content-type": "application/json",
            "accept": "application/json",
        },
        json={
            "model": model,
            "max_tokens": max_tokens,
            "stream": False,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=120,
    )
    latency_ms = (time.time() - start) * 1000

    if resp.status_code != 200:
        print(f"HTTP {resp.status_code}: {resp.text[:300]}")
        sys.exit(1)

    data = resp.json()
    msg = data["choices"][0].get("message", {})
    answer = msg.get("content") or msg.get("reasoning_content") or ""
    if not answer:
        # Reasoning model: budget token habis untuk berpikir
        reasoning = msg.get("reasoning_content") or ""
        print("Jawaban: (kosong — budget token habis untuk reasoning; naikkan -t)")
        if reasoning:
            print(f"Reasoning (terpotong): {reasoning[:300]}")
    else:
        print("\nJawaban:")
        print("=" * 60)
        print(answer)

    usage = data.get("usage")
    if usage:
        print("\nUsage:")
        print(f"  input_tokens     : {usage.get('prompt_tokens', '?')}")
        print(f"  output_tokens    : {usage.get('completion_tokens', '?')}")
        print(f"  total_tokens     : {usage.get('total_tokens', '?')}")
        details = usage.get("completion_tokens_details") or {}
        if details.get("reasoning_tokens"):
            print(f"  reasoning_tokens : {details['reasoning_tokens']}")
    print(f"\nLatency: {latency_ms:.0f} ms")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat HCNSec (OpenAI Compatible)")
    parser.add_argument("-m", "--model", default="DeepSeek-V4-Flash", help="Nama model (case-sensitive) atau auto")
    parser.add_argument("-p", "--pesan", default="hello, who are you?", help="Prompt")
    parser.add_argument("-t", "--tokens", type=int, default=1024, help="Max tokens (>=1024 utk model reasoning)")
    parser.add_argument("--list-models", action="store_true", help="List model tersedia")
    args = parser.parse_args()

    key = get_api_key()
    if not key:
        print(f"Error: {KEY_ENV} tidak ditemukan di env atau .env")
        sys.exit(1)

    if args.list_models:
        list_models(key)
    else:
        chat(key, args.model, args.pesan, args.tokens)
