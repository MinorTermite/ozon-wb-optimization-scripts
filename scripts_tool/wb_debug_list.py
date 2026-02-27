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

def dump_everything():
    url = 'https://content-api.wildberries.ru/content/v2/get/cards/list'
    # Test 1: No filter at all
    print("Test 1: Unfiltered request...")
    payload = {
        "settings": {
            "cursor": { "limit": 100 }
        }
    }
    r = requests.post(url, headers=headers, json=payload)
    if r.status_code == 200:
        data = r.json()
        print(f"Total items in response: {len(data.get('cards', []))}")
        print(f"Cursor total: {data.get('cursor', {}).get('total')}")
        with open('debug_unfiltered_list.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    else:
        print(f"Test 1 Error: {r.status_code} {r.text}")

    # Test 2: withRoot = True
    print("\nTest 2: withRoot=True request...")
    payload = {
        "settings": {
            "cursor": { "limit": 100 },
            "filter": { "withRoot": True }
        }
    }
    r = requests.post(url, headers=headers, json=payload)
    if r.status_code == 200:
        data = r.json()
        print(f"Total items withRoot=True: {len(data.get('cards', []))}")
        print(f"Cursor total: {data.get('cursor', {}).get('total')}")
    else:
        print(f"Test 2 Error: {r.status_code} {r.text}")

if __name__ == "__main__":
    dump_everything()
