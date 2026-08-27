"""[STANDALONE] Chat Poolside via OpenAI Compatible API.

Bisa jalan sendiri: cukup file ini + .env berisi POOLSIDE_API_KEY.
Tidak butuh folder formats/ atau run.py.
Versi terintegrasi (multi-provider): lihat /run.py

Endpoint: POST https://inference.poolside.ai/v1/chat/completions
Model:    poolside/laguna-s-2.1, poolside/laguna-xs-2.1

GOTCHA:
  - TEXT-ONLY: kedua model TIDAK dukung image/video/audio -> 400 multimodal.
  - laguna-xs-2.1 = model reasoning: max_tokens kecil (mis. 32) -> jawaban kosong.
  - API key dibuat via Gmail OAuth di https://platform.poolside.ai/api-keys.
  - Opt-out training: Settings -> 'Opt-out of Poolside using your Content for training'.

Contoh:
  python chat.py -m poolside/laguna-s-2.1 -p "jelaskan LLM dalam 1 kalimat"
  python chat.py --list-models
"""

import argparse
import os
import sys
import time

import requests

BASE_URL = "https://inference.poolside.ai/v1"


def get_api_key():
    key = os.getenv("POOLSIDE_API_KEY")
    if key:
        return key
    here = os.path.dirname(os.path.abspath(__file__))
    for env_path in (os.path.join(here, ".env"), os.path.join(here, "..", "..", ".env")):
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("POOLSIDE_API_KEY="):
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
        },
        json={
            "model": model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=120,
    )
    latency_ms = (time.time() - start) * 1000

    if resp.status_code != 200:
        print(f"HTTP {resp.status_code}: {resp.text[:300]}")
        sys.exit(1)

    data = resp.json()
    print("\nJawaban:")
    print("=" * 60)
    print(data["choices"][0]["message"]["content"])

    usage = data.get("usage")
    if usage:
        print("\nUsage:")
        print(f"  input_tokens     : {usage.get('prompt_tokens', '?')}")
        print(f"  output_tokens    : {usage.get('completion_tokens', '?')}")
        print(f"  total_tokens     : {usage.get('total_tokens', '?')}")
        # Reasoning model (laguna-xs-2.1) bisa mengembalikan reasoning_tokens
        if "completion_tokens_details" in usage:
            details = usage["completion_tokens_details"]
            if "reasoning_tokens" in details:
                print(f"  reasoning_tokens : {details['reasoning_tokens']}")
    print(f"\nLatency: {latency_ms:.0f} ms")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat Poolside (OpenAI Compatible)")
    parser.add_argument("-m", "--model", default="poolside/laguna-s-2.1", help="Nama model")
    parser.add_argument("-p", "--pesan", default="hello, who are you?", help="Prompt")
    parser.add_argument("-t", "--tokens", type=int, default=512, help="Max tokens")
    parser.add_argument("--list-models", action="store_true", help="List model tersedia")
    args = parser.parse_args()

    key = get_api_key()
    if not key:
        print("Error: POOLSIDE_API_KEY tidak ditemukan di env atau .env")
        sys.exit(1)

    if args.list_models:
        list_models(key)
    else:
        chat(key, args.model, args.pesan, args.tokens)
