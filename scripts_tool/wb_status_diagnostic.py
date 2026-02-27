import json
import os
import requests

BASE_DIR = r'C:\Users\GravMix\.gemini\antigravity\playground\core-pulsar'
ENV_PATH = os.path.join(BASE_DIR, '.env')

# Load API key
WB_KEY = ''
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('WB_API_KEY='):
                WB_KEY = line.strip().split('=', 1)[1]
                break

if not WB_KEY:
    print("Error: WB_API_KEY not found")
    exit(1)

headers = {
    'Authorization': WB_KEY,
    'Content-Type': 'application/json'
}

def get_cards_status():
    print("1. Fetching ALL active cards (no root filter)...")
    url = 'https://content-api.wildberries.ru/content/v2/get/cards/list'
    all_cards = []
    cursor = {"limit": 100}
    
    while True:
        payload = {
            "settings": {
                "cursor": cursor,
                "filter": { "withRoot": False }
            }
        }
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        if r.status_code == 200:
            data = r.json()
            cards = data.get('cards', [])
            if not cards: break
            all_cards.extend(cards)
            
            new_cursor = data.get('cursor', {})
            if len(cards) < 100 or new_cursor.get('total', 0) <= len(all_cards):
                break
            cursor = new_cursor
        else:
            print(f"Error fetching cards: {r.status_code} {r.text}")
            break
            
    print(f"Total active cards (NM_ID > 0): {len(all_cards)}")

    print("\n2. Checking ERROR LIST (Drafts) via POST...")
    err_url = 'https://content-api.wildberries.ru/content/v2/cards/error/list'
    payload = {"settings": {"cursor": {"limit": 100}}}
    r = requests.post(err_url, headers=headers, json=payload)
    if r.status_code == 200:
        errors = r.json().get('data', {}).get('cards', []) 
        if not errors and 'data' in r.json():
            if isinstance(r.json()['data'], list): errors = r.json()['data']
            else: errors = r.json().get('data', {}).get('cards', [])
        print(f"Total drafting items (Errors) found: {len(errors)}")
    else:
        print(f"Error fetching error list: {r.status_code} {r.text}")

    print("\n3. Checking PROCESSING BUFFER (/content/v2/buffer/goods/task)...")
    buf_url = 'https://content-api.wildberries.ru/content/v2/buffer/goods/task'
    r = requests.get(buf_url, headers=headers)
    if r.status_code == 200:
        data = r.json().get('data', [])
        print(f"Items being processed in buffer: {len(data)}")
        for b in data[:10]:
            print(f"- Batch: {b.get('batchUUID')}, Status: {b.get('status')}")
    else:
        print(f"Error fetching buffer: {r.status_code} {r.text}")

    print("\n4. Checking TRASH (/content/v2/get/cards/trash)...")
    trash_url = 'https://content-api.wildberries.ru/content/v2/get/cards/trash'
    payload = {"settings": {"cursor": {"limit": 100}}}
    r = requests.post(trash_url, headers=headers, json=payload)
    if r.status_code == 200:
        trash = r.json().get('cards', [])
        print(f"Items in TRASH: {len(trash)}")
    else:
        print(f"Error fetching trash: {r.status_code} {r.text}")

if __name__ == "__main__":
    get_cards_status()

if __name__ == "__main__":
    get_cards_status()
