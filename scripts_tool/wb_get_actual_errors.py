import requests
import json

with open('.env', 'r', encoding='utf-8') as f:
    env = dict(line.strip().split('=', 1) for line in f if '=' in line and not line.startswith('#'))

H = {'Authorization': env['WB_API_KEY'], 'Content-Type': 'application/json'}

def get_errors():
    print("=== FETCHING WB ERRORS ===")
    url = "https://content-api.wildberries.ru/content/v2/cards/error/list"
    payload = {"locale": "ru"}
    r = requests.post(url, headers=H, json=payload)
    if r.status_code == 200:
        data = r.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return data
    else:
        print(f"Error {r.status_code}: {r.text}")
        return None

if __name__ == "__main__":
    get_errors()
