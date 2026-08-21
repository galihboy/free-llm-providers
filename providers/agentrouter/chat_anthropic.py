"""[STANDALONE] Chat AgentRouter via Anthropic Messages API.

Bisa jalan sendiri: cukup file ini + .env berisi AGENTROUTER_API_KEY.
Tidak butuh folder formats/ atau run.py.
Versi terintegrasi (multi-provider): lihat /run.py

Endpoint: POST https://agentrouter.org/v1/messages
Model:    claude-opus-5, claude-opus-4-8, gpt-5.6-sol

GOTCHA:
  - Header user-agent "claude-cli/..." + x-stainless-* WAJIB, kalau tidak 401.
  - Prompt non-Inggris kena 400 content-blocked -> pakai ENGLISH_ANCHOR.
  - Response bisa berisi blok "thinking" (model reasoning) selain "text".

Contoh:
  python chat_anthropic.py -m claude-opus-5 -p "halo, apa kabar?"
"""

import argparse
import os
import sys
import time

import requests

BASE_URL = "https://agentrouter.org"

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
    key = os.getenv("AGENTROUTER_API_KEY")
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
        "x-api-key": api_key,
        "Authorization": f"Bearer {api_key}",
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
        "accept": "application/json",
    }
    headers.update(HEADERS_EXTRA)
    return headers


def chat(api_key, model, prompt, max_tokens=1024):
    print(f"Base URL: {BASE_URL}")
    print(f"Model: {model}")
    print(f"Pesan: {prompt}")
    print("-" * 60)

    start = time.time()
    resp = requests.post(
        f"{BASE_URL}/v1/messages",
        headers=build_headers(api_key),
        json={
            "model": model,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": ENGLISH_ANCHOR}]},
                {"role": "assistant", "content": [{"type": "text", "text": "Understood. I will assist in the user's language."}]},
                {"role": "user", "content": prompt},
            ],
        },
        timeout=120,
    )
    latency_ms = (time.time() - start) * 1000

    if resp.status_code != 200:
        print(f"HTTP {resp.status_code}: {resp.text[:300]}")
        sys.exit(1)

    data = resp.json()

    # Parse content[] — bisa berisi blok text dan/atau thinking
    texts = []
    for c in data.get("content", []):
        if isinstance(c, dict):
            if c.get("type") == "text":
                texts.append(c.get("text", ""))
            elif c.get("type") == "thinking":
                texts.append(c.get("thinking", c.get("text", "")))

    print("\nJawaban:")
    print("=" * 60)
    print("".join(texts) if texts else "(tidak ada teks)")

    usage = data.get("usage")
    if usage:
        print("\nUsage:")
        print(f"  input_tokens     : {usage.get('input_tokens', '?')}")
        print(f"  output_tokens    : {usage.get('output_tokens', '?')}")
    print(f"\nLatency: {latency_ms:.0f} ms")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat AgentRouter (Anthropic Messages)")
    parser.add_argument("-m", "--model", default="claude-opus-5", help="Nama model")
    parser.add_argument("-p", "--pesan", default="halo, apa kabar?", help="Prompt")
    parser.add_argument("-t", "--tokens", type=int, default=1024, help="Max tokens")
    args = parser.parse_args()

    key = get_api_key()
    if not key:
        print("Error: AGENTROUTER_API_KEY tidak ditemukan di env atau .env")
        sys.exit(1)

    chat(key, args.model, args.pesan, args.tokens)
