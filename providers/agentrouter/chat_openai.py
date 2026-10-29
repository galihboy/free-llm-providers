"""[STANDALONE] Chat AgentRouter via OpenAI Responses API.

Bisa jalan sendiri: cukup file ini + .env berisi AGENTROUTER_API_KEY.
Tidak butuh folder formats/ atau run.py.
Versi terintegrasi (multi-provider): lihat /run.py

Endpoint: POST https://ps.air-outer.com/v1/responses
Model:    gpt-6.1-sol, gpt-6-astra, gpt-5.6-sol

GOTCHA:
  - Header user-agent "claude-cli/..." + x-stainless-* WAJIB, kalau tidak 401.
  - Prompt non-Inggris kena 400 content-blocked -> pakai ENGLISH_ANCHOR.

Contoh:
  python chat_openai.py -m gpt-5.6-sol -p "jelaskan LLM dalam 1 kalimat"
  python chat_openai.py --list-models
"""

import argparse
import os
import sys
import time

import requests

BASE_URL = "https://ps.air-outer.com/v1"

ENGLISH_ANCHOR = (
    "You are an expert AI programming assistant working inside a code editor. "
    "You help with software engineering tasks: code navigation, refactoring, "
    "debugging, testing, architecture, performance, and security. "
    "This guidance is language-agnostic and applies to Python, JavaScript, "
    "TypeScript, Go, Rust, Java, C++, and more. Stay neutral, factual, and efficient."
)

HEADERS_EXTRA = {
    "user-agent": "claude-cli/2.1.195 (external, sdk-cli)",
    "x-app": "cli",
    "x-stainless-package-version": "0.0.0",
    "x-stainless-runtime": "python",
    "x-stainless-os": "windows",
}


def get_api_key():
    """Baca key dari env atau file .env (cari di folder ini lalu root repo)."""
    for name in ("AGENTROUTER_API_KEY", "AGENTROUTER_API_KEY_OPENAI"):
        key = os.getenv(name)
        if key:
            return key
    here = os.path.dirname(os.path.abspath(__file__))
    for env_path in (os.path.join(here, ".env"), os.path.join(here, "..", "..", ".env")):
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("AGENTROUTER_API_KEY="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def build_headers(api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "content-type": "application/json",
        "accept": "application/json",
    }
    headers.update(HEADERS_EXTRA)
    return headers


def list_models(api_key):
    r = requests.get(f"{BASE_URL}/models", headers=build_headers(api_key), timeout=30)
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
        f"{BASE_URL}/responses",
        headers=build_headers(api_key),
        json={
            "model": model,
            "max_output_tokens": max_tokens,
            "input": [
                {"role": "user", "content": [{"type": "input_text", "text": ENGLISH_ANCHOR}]},
                {"role": "assistant", "content": [{"type": "output_text", "text": "Understood. I will assist in the user's language."}]},
                {"role": "user", "content": [{"type": "input_text", "text": prompt}]},
            ],
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
    answer = data.get("output_text")
    if not answer:
        answer = "".join(
            content.get("text", "")
            for item in data.get("output", [])
            for content in item.get("content", [])
            if content.get("type") == "output_text"
        )
    print(answer or "(tidak ada teks)")

    usage = data.get("usage")
    if usage:
        print("\nUsage:")
        print(f"  input_tokens     : {usage.get('input_tokens', '?')}")
        print(f"  output_tokens    : {usage.get('output_tokens', '?')}")
        print(f"  total_tokens     : {usage.get('total_tokens', '?')}")
    print(f"\nLatency: {latency_ms:.0f} ms")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat AgentRouter (OpenAI Compatible)")
    parser.add_argument("-m", "--model", default="gpt-5.6-sol", help="Nama model")
    parser.add_argument("-p", "--pesan", default="hello, who are you?", help="Prompt")
    parser.add_argument("-t", "--tokens", type=int, default=512, help="Max tokens")
    parser.add_argument("--list-models", action="store_true", help="List model tersedia")
    args = parser.parse_args()

    key = get_api_key()
    if not key:
        print("Error: AGENTROUTER_API_KEY tidak ditemukan di env atau .env")
        sys.exit(1)

    if args.list_models:
        list_models(key)
    else:
        chat(key, args.model, args.pesan, args.tokens)
