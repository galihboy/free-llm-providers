"""Smoke test semua provider sekaligus -> tabel hasil.

Cara kerja:
  - Baca semua providers/*.yaml
  - Untuk tiap format: list model (live/statis), lalu kirim prompt pendek ke model pertama
  - Skip provider tanpa API key di .env
  - Hasil dicetak sebagai tabel + disimpan ke smoke_result.json

Contoh:
  python tools/smoke_test_all.py
  python tools/smoke_test_all.py --prompt "say OK"
"""

import argparse
import json
import os
import sys
import time

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(ROOT, ".env"))

from formats import FORMAT_CLIENTS
from formats.base import get_api_key, list_models


def smoke_one(provider_name, provider_cfg, fmt_name, fmt_cfg, prompt):
    api_key = get_api_key(fmt_cfg)
    if not api_key:
        return {"status": "SKIP", "detail": f"no key ({fmt_cfg.get('key_env')})"}

    models, source = list_models(fmt_cfg, api_key)
    if not models:
        return {"status": "FAIL", "detail": "no models"}

    model = models[0]
    if fmt_name not in FORMAT_CLIENTS:
        return {"status": "SKIP", "detail": f"format {fmt_name} belum diimplementasikan"}

    client = FORMAT_CLIENTS[fmt_name]
    try:
        result = client.chat(fmt_cfg, model, prompt, max_tokens=64, timeout=60)
    except Exception as e:
        return {"status": "FAIL", "detail": str(e)[:100]}

    if result.get("answer") is None:
        return {"status": "FAIL", "detail": f"HTTP {result.get('status')}: {result.get('error', '')[:80]}"}

    return {
        "status": "OK",
        "model": model,
        "models_source": source,
        "latency_ms": round(result["latency_ms"]),
        "answer_preview": result["answer"][:60].replace("\n", " "),
    }


def main():
    parser = argparse.ArgumentParser(description="Smoke test semua provider")
    parser.add_argument("--prompt", default="say OK", help="Prompt tes pendek")
    parser.add_argument(
        "--skip",
        default=os.getenv("SMOKE_SKIP", ""),
        help="Daftar provider (dipisah koma) yang di-skip. "
             "Berguna di CI kalau IP runner diblokir upstream (mis. AgentRouter).",
    )
    args = parser.parse_args()

    skip = {s.strip() for s in args.skip.split(",") if s.strip()}

    providers_dir = os.path.join(ROOT, "providers")
    results = []

    for fname in sorted(os.listdir(providers_dir)):
        if not fname.endswith(".yaml"):
            continue
        pname = fname[:-5]
        with open(os.path.join(providers_dir, fname), "r", encoding="utf-8") as f:
            pcfg = yaml.safe_load(f)

        for fmt_name, fmt_cfg in pcfg.get("formats", {}).items():
            if pname in skip:
                r = {"status": "SKIP", "detail": "skipped (SMOKE_SKIP)"}
            else:
                r = smoke_one(pname, pcfg, fmt_name, fmt_cfg, args.prompt)
            r.update({"provider": pname, "format": fmt_name})
            results.append(r)
            icon = {"OK": "✅", "FAIL": "❌", "SKIP": "⏭️"}.get(r["status"], "?")
            lat = f"{r['latency_ms']}ms" if "latency_ms" in r else "-"
            print(f"{icon} {pname:15s} {fmt_name:20s} {r.get('model', '-'):25s} {lat:8s} {r.get('detail', r.get('answer_preview', ''))}")

    out = os.path.join(ROOT, "smoke_result.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nHasil disimpan ke: {out}")


if __name__ == "__main__":
    main()
