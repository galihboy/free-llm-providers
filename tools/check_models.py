import os, requests, json
from dotenv import load_dotenv
load_dotenv()
key = os.getenv('AGENTROUTER_API_KEY')

HEADERS = {
    'Authorization': f'Bearer {key}',
    'content-type': 'application/json',
    'user-agent': 'claude-cli/2.1.195 (external, sdk-cli)',
    'x-app': 'cli',
    'x-stainless-package-version': '0.0.0',
    'x-stainless-runtime': 'python',
    'x-stainless-os': 'windows',
}

# Cek model di endpoint OpenAI
print('=== Endpoint OpenAI (/models) ===')
r = requests.get('https://agentrouter.org/v1/models', headers=HEADERS, timeout=30)
print(f'HTTP {r.status_code}')
if r.status_code == 200:
    models = r.json().get('data', [])
    for m in models:
        print(f'  - {m.get("id")}')
    ids = [m.get('id') for m in models]
    if 'gpt-6-astra' in ids:
        print('  >>> gpt-6-astra DITEMUKAN')
    else:
        print('  >>> gpt-6-astra TIDAK ADA di daftar')
else:
    print(r.text[:300])

# Cek model di endpoint Anthropic
print()
print('=== Endpoint Anthropic (/v1/models) ===')
r2 = requests.get('https://agentrouter.org/v1/models', headers=HEADERS, timeout=30)
print(f'HTTP {r2.status_code}')
if r2.status_code == 200:
    models2 = r2.json().get('data', [])
    for m in models2:
        print(f'  - {m.get("id")}')
    ids2 = [m.get('id') for m in models2]
    if 'gpt-6-astra' in ids2:
        print('  >>> gpt-6-astra DITEMUKAN')
    else:
        print('  >>> gpt-6-astra TIDAK ADA di daftar')
