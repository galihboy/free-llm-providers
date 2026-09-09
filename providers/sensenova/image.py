"""[STANDALONE] Generasi dan edit gambar SenseNova.

Bisa jalan sendiri: cukup file ini + .env berisi SENSENOVA_API_KEY.

Contoh:
  python image.py generate -p "seekor kucing merah muda yang lucu"
  python image.py generate -m sensenova-u1-fast -p "infografis tentang AI" -s 2752x1536
  python image.py edit -i sumber.png -p "ubah latar belakang menjadi pegunungan"
"""

import argparse
import base64
import mimetypes
import os
import sys
import time
from pathlib import Path

import requests

BASE_URL = "https://token.sensenova.ai/v1"


def get_api_key():
    key = os.getenv("SENSENOVA_API_KEY")
    if key:
        return key
    here = Path(__file__).resolve().parent
    for env_path in (here / ".env", here / ".." / ".." / ".env"):
        if not env_path.exists():
            continue
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("SENSENOVA_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def request(api_key, endpoint, payload, timeout):
    start = time.time()
    response = requests.post(
        f"{BASE_URL}{endpoint}",
        headers={"Authorization": f"Bearer {api_key}", "content-type": "application/json"},
        json=payload,
        timeout=timeout,
    )
    latency_ms = (time.time() - start) * 1000
    if response.status_code != 200:
        print(f"HTTP {response.status_code}: {response.text[:500]}")
        sys.exit(1)
    return response.json(), latency_ms


def save_images(data, output_dir, prefix):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for index, item in enumerate(data.get("data", []), start=1):
        b64 = item.get("b64_json")
        if b64:
            path = output_dir / f"{prefix}_{index}.png"
            path.write_bytes(base64.b64decode(b64))
            saved.append(path)
            print(f"Disimpan: {path}")
        elif item.get("url"):
            print(f"URL sementara: {item['url']}")
    return saved


def as_image_input(value):
    if value.startswith(("http://", "https://", "data:image/")):
        return value
    path = Path(value)
    if not path.exists():
        raise FileNotFoundError(f"File gambar tidak ditemukan: {value}")
    media_type = mimetypes.guess_type(path.name)[0] or "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{media_type};base64,{encoded}"


def main():
    parser = argparse.ArgumentParser(description="Generasi dan edit gambar SenseNova")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate", help="Buat gambar dari prompt")
    generate.add_argument("-p", "--prompt", required=True)
    generate.add_argument("-m", "--model", default="sensenova-u1.5-lite")
    generate.add_argument("-s", "--size", default="1024x1024")
    generate.add_argument("-o", "--output-dir", default=".")
    generate.add_argument("--watermark", action=argparse.BooleanOptionalAction, default=True)
    generate.add_argument("--no-prompt-extend", action="store_true")

    edit = subparsers.add_parser("edit", help="Edit gambar dari URL atau file lokal")
    edit.add_argument("-i", "--image", required=True, help="URL atau path file gambar")
    edit.add_argument("-p", "--prompt", required=True)
    edit.add_argument("-o", "--output-dir", default=".")
    edit.add_argument("--watermark", action=argparse.BooleanOptionalAction, default=True)
    edit.add_argument("--no-prompt-extend", action="store_true")

    args = parser.parse_args()
    api_key = get_api_key()
    if not api_key:
        print("Error: SENSENOVA_API_KEY tidak ditemukan di env atau .env")
        sys.exit(1)

    if args.command == "generate":
        payload = {
            "model": args.model,
            "prompt": args.prompt,
            "n": 1,
            "size": args.size,
            "response_format": "b64_json",
            "output_format": "png",
            "watermark": args.watermark,
            "prompt_extend": not args.no_prompt_extend,
        }
        data, latency_ms = request(api_key, "/images/generations", payload, 180)
        prefix = "sensenova_generation_" + time.strftime("%Y%m%d_%H%M%S")
    else:
        try:
            image_input = as_image_input(args.image)
        except (FileNotFoundError, OSError) as error:
            print(f"Error: {error}")
            sys.exit(1)
        payload = {
            "model": "sensenova-u1.5-lite",
            "images": [{"image_url": image_input}],
            "prompt": args.prompt,
            "n": 1,
            "size": "auto",
            "response_format": "b64_json",
            "watermark": args.watermark,
            "prompt_extend": not args.no_prompt_extend,
        }
        data, latency_ms = request(api_key, "/images/edits", payload, 180)
        prefix = "sensenova_edit_" + time.strftime("%Y%m%d_%H%M%S")

    saved = save_images(data, args.output_dir, prefix)
    print(f"Selesai: {len(saved)} gambar, latency {latency_ms:.0f} ms")


if __name__ == "__main__":
    main()
