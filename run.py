"""[FRAMEWORK] CLI universal multi-provider.

Cuma butuh 1 provider? Baca providers/<nama>/README.md (lebih sederhana).

Contoh:
  python run.py --provider agentrouter --format openai_chat -m gpt-5.6-sol -p "jelaskan LLM"
  python run.py --provider agentrouter --format anthropic_messages -m claude-opus-5 -p "halo"
  python run.py --provider groq -p "hello"
  python run.py --provider agentrouter --list-models
"""

import argparse
import os
import sys

import yaml
from dotenv import load_dotenv

from formats import FORMAT_CLIENTS
from formats.base import list_models

ROOT = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(ROOT, ".env"))


def load_provider(name):
    path = os.path.join(ROOT, "providers", f"{name}.yaml")
    if not os.path.exists(path):
        avail = [
            f[:-5] for f in os.listdir(os.path.join(ROOT, "providers"))
            if f.endswith(".yaml")
        ]
        print(f"Error: provider '{name}' tidak ditemukan.")
        print(f"Provider tersedia: {', '.join(sorted(avail))}")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def pick_format(provider_name, provider_cfg, format_name):
    formats = provider_cfg.get("formats", {})
    if format_name:
        if format_name not in formats:
            print(f"Error: format '{format_name}' tidak ada di provider ini.")
            print(f"Format tersedia: {', '.join(formats.keys())}")
            sys.exit(1)
        fmt_name, fmt_cfg = format_name, formats[format_name]
    else:
        # Default: format pertama yang dideklarasikan
        fmt_name = next(iter(formats))
        fmt_cfg = formats[fmt_name]
    # Folder anchor lokal provider (menang atas anchors/ global)
    fmt_cfg = dict(fmt_cfg)
    fmt_cfg["anchor_dirs"] = [
        os.path.join(ROOT, "providers", provider_name, "anchors")
    ]
    return fmt_name, fmt_cfg


def main():
    parser = argparse.ArgumentParser(
        description="CLI universal multi-provider LLM gratis",
        epilog="Untuk panduan per-provider, baca providers/<nama>/README.md",
    )
    parser.add_argument("--provider", help="Nama provider (misal: agentrouter)")
    parser.add_argument("--format", dest="fmt", help="Format API (default: format pertama di YAML)")
    parser.add_argument("-m", "--model", help="Nama model (default: model pertama di YAML)")
    parser.add_argument("-p", "--pesan", help="Prompt")
    parser.add_argument("-t", "--tokens", type=int, default=512, help="Max tokens")
    parser.add_argument(
        "--anchor",
        help="Anchor utk provider bermoderasi: nama varian bawaan "
        "(general/coding/extraction/text2sql/eval) ATAU nama file di anchors/ "
        "(misal custom_chat). Menimpa deklarasi YAML.",
    )
    parser.add_argument(
        "--list-anchors", action="store_true",
        help="Tampilkan semua anchor yang tersedia (bawaan + file anchors/*.yaml)",
    )
    parser.add_argument("--list-models", action="store_true", help="List model tersedia")
    args = parser.parse_args()

    if args.list_anchors:
        from formats.base import ANCHORS, ANCHORS_DIR, list_anchor_files

        print("Anchor bawaan (registry di formats/base.py):")
        for nama in ANCHORS:
            print(f"  - {nama}")
        print("Anchor file global (anchors/*.yaml):")
        for nama in list_anchor_files([ANCHORS_DIR]):
            print(f"  - {nama}")
        if args.provider:
            local_dir = os.path.join(ROOT, "providers", args.provider, "anchors")
            local = list_anchor_files([local_dir])
            if local:
                print(f"Anchor file lokal (providers/{args.provider}/anchors/):")
                for nama in local:
                    print(f"  - {nama}  (menang atas global kalau nama sama)")
        return

    if not args.provider:
        parser.error("--provider wajib diisi (kecuali --list-anchors)")

    provider_cfg = load_provider(args.provider)
    fmt_name, fmt_cfg = pick_format(args.provider, provider_cfg, args.fmt)

    # Override varian anchor dari CLI (kalau diminta)
    if args.anchor:
        fmt_cfg = dict(fmt_cfg)  # salin agar YAML asli tidak berubah
        mod = dict(fmt_cfg.get("moderation", {}))
        mod["english_anchor"] = args.anchor
        fmt_cfg["moderation"] = mod

    if fmt_name not in FORMAT_CLIENTS:
        print(f"Error: format '{fmt_name}' belum diimplementasikan di formats/.")
        sys.exit(1)

    if args.list_models:
        from formats.base import get_api_key

        api_key = get_api_key(fmt_cfg)
        if not api_key:
            print(f"Error: API key tidak ditemukan untuk env var: {fmt_cfg.get('key_env')}")
            sys.exit(1)
        models, source = list_models(fmt_cfg, api_key)
        label = {"live": "[LIVE]", "static": "[STATIC]", "static-fallback": "[STATIC-FALLBACK]"}
        print(f"Model {provider_cfg['name']} {label.get(source, '')}:")
        for m in models:
            print(f"  - {m}")
        return

    if not args.pesan:
        print("Error: berikan prompt dengan -p/--pesan (atau pakai --list-models)")
        sys.exit(1)

    model = args.model or fmt_cfg.get("models", [None])[0]
    if not model:
        print("Error: tidak ada model. Sebutkan dengan -m atau isi 'models' di YAML.")
        sys.exit(1)

    client = FORMAT_CLIENTS[fmt_name]
    print(f"Provider: {provider_cfg['name']}")
    print(f"Format  : {fmt_name}")
    print(f"Model   : {model}")
    print(f"Pesan   : {args.pesan}")
    print("-" * 60)

    result = client.chat(fmt_cfg, model, args.pesan, max_tokens=args.tokens)

    if result.get("answer") is None:
        print(f"HTTP {result.get('status')}: {result.get('error', '')}")
        sys.exit(1)

    print("\nJawaban:")
    print("=" * 60)
    print(result["answer"])

    usage = result.get("usage")
    if usage:
        print("\nUsage:")
        print(f"  input_tokens     : {usage.get('input_tokens', usage.get('prompt_tokens', '?'))}")
        print(f"  output_tokens    : {usage.get('output_tokens', usage.get('completion_tokens', '?'))}")
        print(f"  total_tokens     : {usage.get('total_tokens', '?')}")
    print(f"\nLatency: {result['latency_ms']:.0f} ms")


if __name__ == "__main__":
    main()
