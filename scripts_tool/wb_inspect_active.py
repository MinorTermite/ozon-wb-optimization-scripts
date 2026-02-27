import requests
import json
import os

BASE_DIR = r'C:\Users\GravMix\.gemini\antigravity\playground\core-pulsar'
ENV_PATH = os.path.join(BASE_DIR, '.env')

WB_KEY = ''
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('WB_API_KEY='):
                WB_KEY = line.strip().split('=', 1)[1]
                break

headers = {'Authorization': WB_KEY, 'Content-Type': 'application/json'}

def inspect_active():
    # NM 296462523 or similar
    payload = {
        "settings": {
            "filter": {
                "withRoot": True
            },
            "cursor": {
                "limit": 100
            }
        }
    }
    r = requests.post('https://content-api.wildberries.ru/content/v2/get/cards/list', headers=headers, json=payload)
    if r.status_code == 200:
        cards = r.json().get('cards', [])
        for c in cards:
            if c.get('nmID') == 296462523:
                print(f"Found card {c.get('nmID')}")
                print(json.dumps(c, ensure_ascii=False, indent=2))
                break
        else:
            print("Card not found in active list.")
            if cards:
                print("Inspecting first card for schema:")
                print(json.dumps(cards[0], ensure_ascii=False, indent=2))
    else:
        print(f"Error {r.status_code}: {r.text}")

if __name__ == "__main__":
    inspect_active()
