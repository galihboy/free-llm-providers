"""[SCRATCH] Verifikasi spesifikasi 3 model lama AgentRouter:
claude-opus-5, claude-opus-4-8, gpt-5.6-sol.

Tes: (1) tool calling, (2) vision, (3) probe max_tokens utk tahu batas output.
Bukan bagian repo — boleh dihapus setelah selesai.
"""

import json
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

ANCHOR = (
    "You are a helpful multilingual assistant. Respond accurately and in the "
    "same language the user writes in. Stay neutral, factual, and precise."
)
ACK = "Understood. I will assist in the user's language."

PNG_1PX = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ"
    "AAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)

MODELS = ["claude-opus-5", "claude-opus-4-8", "gpt-5.6-sol"]


def call(model, messages, max_tokens=256, tools=None):
    body = {"model": model, "max_tokens": max_tokens, "messages": messages}
    if tools:
        body["tools"] = tools
    return requests.post(f"{BASE}/chat/completions", headers=HEADERS, json=body, timeout=180)


def msgs(user_content):
    return [
        {"role": "user", "content": ANCHOR},
        {"role": "assistant", "content": ACK},
        {"role": "user", "content": user_content},
    ]


TOOL_DEF = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather for a city",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
        },
    },
}]


def test_tool(model):
    r = call(model, msgs("What is the weather in Bandung? Use the tool."), tools=TOOL_DEF)
    if r.status_code != 200:
        return f"HTTP {r.status_code}: {r.text[:250]}"
    ch = r.json()["choices"][0]
    tc = ch["message"].get("tool_calls")
    if tc:
        return f"YA — {tc[0]['function']['name']}({tc[0]['function']['arguments']})"
    return f"TIDAK — teks: {str(ch['message'].get('content'))[:100]}"


def test_vision(model):
    content = [
        {"type": "text", "text": "What color is this image? Answer in one word."},
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{PNG_1PX}"}},
    ]
    r = call(model, msgs(content))
    if r.status_code != 200:
        return f"HTTP {r.status_code}: {r.text[:250]}"
    return f"MUNGKIN YA — jawab: {str(r.json()['choices'][0]['message'].get('content'))[:100]}"


def test_max_tokens(model, probe):
    r = call(model, msgs("Say OK"), max_tokens=probe)
    if r.status_code != 200:
        return f"max_tokens={probe} -> HTTP {r.status_code}: {r.text[:300]}"
    u = r.json().get("usage", {})
    return f"max_tokens={probe} -> OK (output_tokens={u.get('completion_tokens')})"


if __name__ == "__main__":
    for m in MODELS:
        print("=" * 60)
        print(f"MODEL: {m}")
        print(f"  tool calling : {test_tool(m)}")
        print(f"  vision       : {test_vision(m)}")
        print(f"  probe output : {test_max_tokens(m, 1000000)}")
