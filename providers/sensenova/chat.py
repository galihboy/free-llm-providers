"""[STANDALONE] Chat SenseNova via OpenAI atau Anthropic API.

Bisa jalan sendiri: cukup file ini + .env berisi SENSENOVA_API_KEY.
Versi terintegrasi (multi-provider): lihat /run.py

Contoh:
  python chat.py -p "jelaskan LLM dalam satu kalimat"
  python chat.py --api anthropic -p "Hello!"
  python chat.py --list-models
"""

import argparse
import json
import os
import sys
import time

import requests

OPENAI_BASE_URL = "https://token.sensenova.ai/v1"
ANTHROPIC_BASE_URL = "https://token.sensenova.ai"
DEFAULT_MODEL = "sensenova-6.8-flash-lite"


def get_api_key():
    key = os.getenv("SENSENOVA_API_KEY")
    if key:
        return key
    here = os.path.dirname(os.path.abspath(__file__))
    for env_path in (os.path.join(here, ".env"), os.path.join(here, "..", "..", ".env")):
        if not os.path.exists(env_path):
            continue
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("SENSENOVA_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def list_models(api_key):
    response = requests.get(
        f"{OPENAI_BASE_URL}/models",
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=30,
    )
    if response.status_code != 200:
        print(f"HTTP {response.status_code}: {response.text[:300]}")
        sys.exit(1)
    for model in response.json().get("data", []):
        print(f"- {model.get('id')}")


def chat_openai(api_key, model, prompt, max_tokens):
    url = f"{OPENAI_BASE_URL}/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
    }
    response = requests.post(
        url,
        headers={"Authorization": f"Bearer {api_key}", "content-type": "application/json"},
        json=payload,
        timeout=120,
    )
    if response.status_code != 200:
        return response.status_code, response.text[:500], None, None
    data = response.json()
    message = data.get("choices", [{}])[0].get("message", {})
    answer = message.get("content") or message.get("reasoning") or ""
    return response.status_code, answer, data.get("usage"), data


def chat_anthropic(api_key, model, prompt, max_tokens):
    url = f"{ANTHROPIC_BASE_URL}/v1/messages"
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    response = requests.post(
        url,
        headers={"Authorization": f"Bearer {api_key}", "content-type": "application/json"},
        json=payload,
        timeout=120,
    )
    if response.status_code != 200:
        return response.status_code, response.text[:500], None, None
    data = response.json()
    text = "".join(
        block.get("text", "") for block in data.get("content", []) if block.get("type") == "text"
    )
    return response.status_code, text, data.get("usage"), data


def main():
    parser = argparse.ArgumentParser(description="Chat SenseNova standalone")
    parser.add_argument("-p", "--pesan", default="Hello!", help="Prompt")
    parser.add_argument("-m", "--model", default=DEFAULT_MODEL, help="ID model")
    parser.add_argument("--api", choices=("openai", "anthropic"), default="openai")
    parser.add_argument("-t", "--tokens", type=int, default=512, help="Max token output")
    parser.add_argument("--list-models", action="store_true", help="Tampilkan model tersedia")
    args = parser.parse_args()

    api_key = get_api_key()
    if not api_key:
        print("Error: SENSENOVA_API_KEY tidak ditemukan di env atau .env")
        sys.exit(1)
    if args.list_models:
        list_models(api_key)
        return

    start = time.time()
    if args.api == "anthropic":
        status, answer, usage, raw = chat_anthropic(api_key, args.model, args.pesan, args.tokens)
    else:
        status, answer, usage, raw = chat_openai(api_key, args.model, args.pesan, args.tokens)
    latency_ms = (time.time() - start) * 1000

    if status != 200:
        print(f"HTTP {status}: {answer}")
        sys.exit(1)
    print(answer)
    if usage:
        print(f"\nUsage: {json.dumps(usage, ensure_ascii=False)}")
    print(f"Latency: {latency_ms:.0f} ms")


if __name__ == "__main__":
    main()
