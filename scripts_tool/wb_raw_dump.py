import json
import requests
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

def dump_raw_data():
    url = 'https://content-api.wildberries.ru/content/v2/get/cards/list'
    payload = {
        "settings": {
            "cursor": { "limit": 100 },
            "filter": { "withRoot": False }
        }
    }
    r = requests.post(url, headers=headers, json=payload)
    if r.status_code == 200:
        data = r.json()
        print("Success. Writing raw_cards_list_dump.json")
        with open('raw_cards_list_dump.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    else:
        print(f"Error: {r.status_code} {r.text}")

if __name__ == "__main__":
    dump_raw_data()
