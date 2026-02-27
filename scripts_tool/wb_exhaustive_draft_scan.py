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

def exhaustive_scan():
    url = 'https://content-api.wildberries.ru/content/v2/get/cards/list'
    # Fetch all cards to find if some are missing nmId or have a specific status
    all_cards = []
    cursor = {"limit": 100}
    
    print("Fetching all cards to find hidden drafts...")
    while True:
        payload = {"settings": {"cursor": cursor}}
        r = requests.post(url, headers=headers, json=payload)
        if r.status_code != 200:
            print(f"Error fetching: {r.status_code} {r.text}")
            break
            
        data = r.json()
        cards = data.get('cards', [])
        all_cards.extend(cards)
        
        cursor = data.get('cursor', {})
        if not cursor.get('nmID') or len(cards) < 100:
            break
    
    print(f"Total cards fetched: {len(all_cards)}")
    
    # Analyze cards
    drafts_in_list = [c for c in all_cards if c.get('nmID') == 0]
    print(f"Cards without NM_ID (technical drafts): {len(drafts_in_list)}")
    
    for d in drafts_in_list[:5]:
        print(f"- Vendor: {d.get('vendorCode')}, imtID: {d.get('imtID')}")

    # Check the "Buffer" again with more detail
    print("\nChecking Buffer more deeply...")
    buf_url = 'https://content-api.wildberries.ru/content/v2/buffer/goods/task'
    r = requests.get(buf_url, headers=headers)
    if r.status_code == 200:
        buffer_data = r.json().get('data', [])
        print(f"Items in buffer: {len(buffer_data)}")
        for b in buffer_data:
            # Buffer status can be 'In Process', 'Error', etc.
            print(f"- Task: {b.get('taskId')}, Status: {b.get('status')}")

if __name__ == "__main__":
    exhaustive_scan()
