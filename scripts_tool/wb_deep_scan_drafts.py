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

def deep_scan():
    # 1. Error List
    print("--- Checking Error List ---")
    payload = {"settings": {"cursor": {"limit": 100}}}
    r = requests.post('https://content-api.wildberries.ru/content/v2/cards/error/list', headers=headers, json=payload)
    if r.status_code == 200:
        cards = r.json().get('data', {}).get('cards', [])
        print(f"Errors found: {len(cards)}")
        for c in cards[:5]:
            print(f"- {c.get('vendorCode')}: {c.get('errors')}")
    
    # 2. History of uploads
    print("\n--- Checking Upload History ---")
    r = requests.get('https://content-api.wildberries.ru/content/v2/history/goods/task?limit=10&offset=0', headers=headers)
    if r.status_code == 200:
        tasks = r.json().get('data', [])
        print(f"Recent tasks: {len(tasks)}")
        for t in tasks[:5]:
            print(f"- Task: {t.get('taskId')}, Status: {t.get('status')}")

    # 3. Buffer
    print("\n--- Checking Buffer ---")
    r = requests.get('https://content-api.wildberries.ru/content/v2/buffer/goods/task', headers=headers)
    if r.status_code == 200:
        buffer = r.json().get('data', [])
        print(f"Items in buffer: {len(buffer)}")
        
    # 4. Check specifically if any items have NM_ID=0 in the main list
    print("\n--- Checking Main List for NM_ID=0 ---")
    payload = {"settings": {"cursor": {"limit": 100}}}
    r = requests.post('https://content-api.wildberries.ru/content/v2/get/cards/list', headers=headers, json=payload)
    if r.status_code == 200:
        cards = r.json().get('cards', [])
        drafts = [c for c in cards if c.get('nmID') == 0]
        print(f"Active items with NM_ID=0: {len(drafts)}")

if __name__ == "__main__":
    deep_scan()
