"""[SCRATCH] Probe batas INPUT token glm-5.3 & deepseek-v4-flash di AgentRouter."""

import os

import requests
from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT, ".env"))

KEY = os.getenv("AGENTROUTER_API_KEY")
BASE = "https://agentrouter.org/v1"
HEADERS = {
    "Authorization": f"Bearer {KEY}",
    "content-type": "application/json",
    "user-agent": "claude-cli/2.1.195 (external, sdk-cli)",
    "x-app": "cli",
    "x-stainless-package-version": "0.0.0",
    "x-stainless-runtime": "python",
    "x-stainless-os": "windows",
}

# ~1 token ≈ 4 char utk teks Inggris berulang
UNIT = "The quick brown fox jumps over the lazy dog. "  # 45 char ≈ 18 token (hasil kalibrasi)


def probe(model, n_tokens_approx, max_tokens=16, tok_per_unit=18):
    text = UNIT * (n_tokens_approx // tok_per_unit)
    body = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": f"Repeat OK. {text} Reply OK only."}],
    }
    try:
        r = requests.post(f"{BASE}/chat/completions", headers=HEADERS, json=body, timeout=300)
    except Exception as e:
        return f"~{n_tokens_approx} tok -> EXC {e}"
    if r.status_code != 200:
        return f"~{n_tokens_approx} tok -> HTTP {r.status_code}: {r.text[:300]}"
    u = r.json().get("usage", {})
    return f"~{n_tokens_approx} tok -> OK (prompt_tokens={u.get('prompt_tokens')})"


if __name__ == "__main__":
    # gpt-5.6-sol: 1 unit ≈ 10 token (kalibrasi dari hasil sebelumnya)
    print("== gpt-5.6-sol (cari batas atas, kalibrasi 10 tok/unit) ==")
    print(" ", probe("gpt-5.6-sol", 1_000_000, tok_per_unit=10))
    print(" ", probe("gpt-5.6-sol", 1_100_000, tok_per_unit=10))
