"""[FRAMEWORK] Helper bersama untuk semua format API.

Cuma butuh 1 provider? Lihat providers/<nama>/README.md (lebih sederhana).

Semua field opsional di YAML ditangani di sini:
- extra_headers  : hanya di-merge kalau dideklarasikan
- english_anchor : hanya di-prepend kalau moderation.english_anchor = true
- list_models    : capability opsional; kalau off → pakai daftar statis YAML
"""

import os

import requests
import yaml

# Anchor bahasa Inggris untuk provider dengan moderasi bahasa (misal AgentRouter).
# Prompt non-Inggris bisa kena "content-blocked" tanpa anchor ini.
#
# Anchor punya 2 fungsi:
#   1. (wajib) membuat konteks dominan bahasa Inggris agar lolos moderasi
#   2. (sampingan) mengarahkan persona/tugas — pilih varian sesuai kebutuhan
#
# Sumber anchor (prioritas dari tinggi ke rendah):
#   1. moderation.anchor_text: "teks bebas"   -> override penuh
#   2. moderation.anchor_file: "nama"         -> file anchors/<nama>.yaml
#   3. moderation.english_anchor: <nama|true> -> registry ANCHORS di bawah
#
# File anchor YAML ada di folder anchors/ (bisa ditambah sendiri tanpa edit kode).
ANCHORS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "anchors")

ANCHORS = {
    # Netral untuk tugas umum (default saat english_anchor: true)
    "general": (
        "You are a helpful multilingual assistant. Respond accurately and in the "
        "same language the user writes in. This conversation may cover any topic: "
        "general knowledge, writing, analysis, data extraction, evaluation, SQL, "
        "and more. Stay neutral, factual, and precise."
    ),
    # Tugas coding / software engineering
    "coding": (
        "You are an expert AI programming assistant working inside a code editor. "
        "You help with software engineering tasks: code navigation, refactoring, "
        "debugging, testing, architecture, performance, and security. "
        "This guidance is language-agnostic and applies to Python, JavaScript, "
        "TypeScript, Go, Rust, Java, C++, and more. Stay neutral, factual, and efficient."
    ),
    # Ekstraksi informasi dari teks
    "extraction": (
        "You are a precise data extraction engine. Extract the requested "
        "information exactly as it appears in the source text, without adding, "
        "guessing, or omitting details. Output only the requested format "
        "(JSON, table, or fields) unless the user asks for explanation."
    ),
    # Konversi bahasa alami ke SQL
    "text2sql": (
        "You are a SQL expert. Convert natural language questions into correct, "
        "efficient SQL queries for the given schema. Use standard SQL unless a "
        "dialect is specified. Output only valid SQL unless the user asks for "
        "explanation."
    ),
    # Evaluasi / penilaian konten
    "eval": (
        "You are an impartial evaluator. Score or judge the given content strictly "
        "according to the provided rubric or criteria. Give the verdict first, "
        "then a brief factual justification. Be consistent and objective."
    ),
}

# Alias lama agar kode/dokumentasi lama tetap jalan
ENGLISH_ANCHOR = ANCHORS["coding"]

ANCHOR_ACK = "Understood. I will assist in the user's language."


def load_anchor_file(name, search_dirs=None):
    """Muat anchor dari file <name>.yaml. Return teks prompt atau None.

    Urutan pencarian: tiap folder di search_dirs (misal folder anchor
    provider-lokal providers/<nama>/anchors/), lalu folder global anchors/.
    File lokal menang atas global kalau namanya sama.

    Format file:
      name: <nama>
      description: <deskripsi singkat>
      prompt: >-
        Teks anchor bahasa Inggris ...
    """
    dirs = list(search_dirs or []) + [ANCHORS_DIR]
    for d in dirs:
        path = os.path.join(d, f"{name}.yaml")
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        prompt = data.get("prompt")
        if isinstance(prompt, str) and prompt.strip():
            return prompt.strip()
    return None


def list_anchor_files(dirs):
    """Daftar nama file anchor (*.yaml) di folder-folder yang diberikan.

    Dedup berdasarkan nama; urutan folder menentukan prioritas.
    """
    seen = []
    for d in dirs or []:
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if f.endswith(".yaml") and not f.startswith("_"):
                nama = f[:-5]
                if nama not in seen:
                    seen.append(nama)
    return seen


def get_anchor(cfg):
    """Ambil teks anchor sesuai deklarasi YAML. Return None kalau moderasi off.

    Dukungan konfigurasi (prioritas dari tinggi ke rendah):
      moderation.anchor_text: "teks bebas"  -> override penuh
      moderation.anchor_file: "nama"        -> file <nama>.yaml
      moderation.english_anchor: true       -> varian "general" (registry)
      moderation.english_anchor: <nama>     -> registry ANCHORS, fallback ke file

    Pencarian file anchor (cfg["anchor_dirs"], diisi otomatis oleh run.py/proxy):
      1. providers/<nama>/anchors/<nama>.yaml  (lokal provider, menang)
      2. anchors/<nama>.yaml                   (global, fallback)
    """
    mod = cfg.get("moderation", {})
    search_dirs = cfg.get("anchor_dirs") or []
    anchor = mod.get("english_anchor")
    if not anchor and not mod.get("anchor_text") and not mod.get("anchor_file"):
        return None
    # 1. Teks bebas menang atas semua
    if mod.get("anchor_text"):
        return mod["anchor_text"]
    # 2. File anchor eksplisit
    if mod.get("anchor_file"):
        text = load_anchor_file(mod["anchor_file"], search_dirs)
        if text:
            return text
        raise ValueError(
            f"anchor_file '{mod['anchor_file']}' tidak ditemukan. "
            f"Tersedia: {', '.join(list_anchor_files(search_dirs + [ANCHORS_DIR]))}"
        )
    # 3. english_anchor: true -> default general
    if anchor is True:
        return ANCHORS["general"]
    # 4. english_anchor: "<nama>" -> registry dulu, lalu file (lokal -> global)
    if isinstance(anchor, str):
        if anchor in ANCHORS:
            return ANCHORS[anchor]
        text = load_anchor_file(anchor, search_dirs)
        if text:
            return text
        # String tak dikenal dianggap teks anchor langsung
        return anchor
    return ANCHORS["general"]


def get_api_key(cfg):
    """Ambil API key dari env var sesuai deklarasi YAML (dengan fallback .env manual).

    Urutan pencarian: key_env -> key_env_alt (kalau dideklarasikan).
    """
    candidates = [cfg.get("key_env", "")]
    if cfg.get("key_env_alt"):
        candidates.append(cfg["key_env_alt"])

    for key_env in candidates:
        if not key_env:
            continue
        key = os.getenv(key_env)
        if key:
            return key
        # Fallback: baca langsung dari file .env (kalau load_dotenv belum dipanggil)
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(f"{key_env}="):
                        key = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if key:
                            return key
    return None


def build_headers(cfg, api_key):
    """Header standar + extra_headers opsional dari YAML."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "content-type": "application/json",
        "accept": "application/json",
    }
    # Hanya tambahkan kalau dideklarasikan di YAML (default = header standar saja)
    headers.update(cfg.get("extra_headers", {}))
    return headers


def list_models(cfg, api_key, timeout=30):
    """List model: live kalau capability aktif, fallback statis kalau tidak/gagal.

    Return: (list_model_ids, sumber) dengan sumber = 'live' | 'static' | 'static-fallback'
    """
    lm = cfg.get("list_models")
    static = cfg.get("models", [])

    if not lm:
        # Capability off → pakai daftar statis dari YAML
        return static, "static"

    headers = build_headers(cfg, api_key)
    url = cfg["base_url"].rstrip("/") + lm["endpoint"]
    try:
        r = requests.request(
            lm.get("method", "GET"), url, headers=headers, timeout=timeout
        )
        if r.status_code != 200:
            return static, "static-fallback"
        data = r.json()
        ids = [m.get("id") for m in data.get("data", []) if isinstance(m, dict)]
        return ids or static, "live" if ids else "static-fallback"
    except requests.exceptions.RequestException:
        return static, "static-fallback"
