import os
import requests
from dotenv import load_dotenv

load_dotenv()
key = os.getenv('AGENTROUTER_API_KEY')
H = {
    'Authorization': f'Bearer {key}',
    'content-type': 'application/json',
    'user-agent': 'claude-cli/2.1.195 (external, sdk-cli)',
    'x-app': 'cli',
    'x-stainless-package-version': '0.0.0',
    'x-stainless-runtime': 'python',
    'x-stainless-os': 'windows',
}


def test_model(model_name, max_tokens, prompt_text):
    print(f'=== {model_name} - max_tokens={max_tokens} ===')
    r = requests.post(
        'https://agentrouter.org/v1/chat/completions',
        headers=H,
        json={
            'model': model_name,
            'max_tokens': max_tokens,
            'messages': [
                {'role': 'user', 'content': prompt_text}
            ]
        },
        timeout=120
    )
    status = r.status_code
    if status == 200:
        d = r.json()
        usage = d.get('usage', {})
        rtext = d.get('choices', [{}])[0].get('message', {})
        reasoning = usage.get('reasoning_tokens', 0)
        text_tokens = usage.get('completion_tokens_details', {}).get('text_tokens', 0)
        finish = d.get('choices', [{}])[0].get('finish_reason')
        content = rtext.get('content', '')
        print(f'HTTP {status}')
        print(f'Finish reason: {finish}')
        print(f'Reasoning tokens: {reasoning}')
        print(f'Text tokens: {text_tokens}')
        print(f'Content preview: {content[:400]}')
    else:
        print(f'HTTP {status}: {r.text[:300]}')
    print()


# Test A: gpt-6-astra with higher max_tokens and complex reasoning prompt
test_model('gpt-6-astra', 2048,
    'You are a reasoning engine. Think step by step. Answer: Is gpt-6-astra a reasoning model? Explain advantages and disadvantages of reasoning models.'
)

# Test B: deepseek-v4-flash (known reasoning) with higher max_tokens
test_model('deepseek-v4-flash', 2048,
    'You are a reasoning engine. Think step by step. Answer: Is gpt-6-astra a reasoning model? Explain advantages and disadvantages of reasoning models.'
)

# Test C: gpt-6-astra with very small max_tokens=16 (edge case)
test_model('gpt-6-astra', 16,
    'Answer: OK'
)

# Test D: gpt-6-astra simple response (backward compat check)
test_model('gpt-6-astra', 64,
    'Say OK'
)
