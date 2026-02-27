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

def full_audit():
    print("=== STARTING FULL CATALOG AUDIT ===")
    
    # 1. Active Cards (POST /content/v2/get/cards/list)
    print("\n1. Fetching ALL Active Cards...")
    all_active = []
    cursor = {"limit": 100}
    while True:
        payload = {"settings": {"cursor": cursor}}
        r = requests.post('https://content-api.wildberries.ru/content/v2/get/cards/list', headers=headers, json=payload)
        if r.status_code != 200: break
        data = r.json()
        cards = data.get('cards', [])
        all_active.extend(cards)
        cursor = data.get('cursor', {})
        if not cursor.get('nmID') or len(cards) < 100: break
    print(f"Total Active Cards in API: {len(all_active)}")

    # 2. Error List (POST /content/v2/cards/error/list)
    print("\n2. Checking Error List (Drafts)...")
    payload = {"settings": {"cursor": {"limit": 100}}}
    r = requests.post('https://content-api.wildberries.ru/content/v2/cards/error/list', headers=headers, json=payload)
    if r.status_code == 200:
        errors = r.json().get('data', {}).get('cards', [])
        print(f"Total Errors (Drafts) in API: {len(errors)}")
        for e in errors[:10]:
            print(f"- {e.get('vendorCode')}: {e.get('errors')}")
    else:
        print(f"Error fetching errors: {r.status_code}")

    # 3. Buffer (GET /content/v2/buffer/goods/task)
    print("\n3. Checking Processing Buffer...")
    r = requests.get('https://content-api.wildberries.ru/content/v2/buffer/goods/task', headers=headers)
    if r.status_code == 200:
        buffer = r.json().get('data', [])
        print(f"Items in Processing Buffer: {len(buffer)}")
        for b in buffer[:5]:
            print(f"- Task: {b.get('taskId')}, Status: {b.get('status')}")

    # 4. Check for _v3 specifically
    v3_count = len([c for c in all_active if str(c.get('vendorCode', '')).endswith('_v3')])
    print(f"\n_v3 Cards already Active: {v3_count}")

    print("\n=== AUDIT COMPLETE ===")

if __name__ == "__main__":
    full_audit()
