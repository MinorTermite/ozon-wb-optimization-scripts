import os
import requests
import json
import time

env_path = '.env'
WB_KEY = ''
if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('WB_API_KEY='):
                WB_KEY = line.strip().split('=', 1)[1]
                break

if not WB_KEY:
    print("Error: WB_API_KEY not found in .env")
    exit(1)

headers = {
    'Authorization': WB_KEY,
    'Content-Type': 'application/json'
}

print('Fetching all WB cards...')
all_cards = []
cursor = {"limit": 100}

while True:
    payload = {'settings': {'cursor': cursor, 'filter': {'withPhoto': -1}}}
    r = requests.post('https://content-api.wildberries.ru/content/v2/get/cards/list', 
                      headers=headers, 
                      json=payload)
    
    if r.status_code != 200:
        print(f"Error: {r.status_code} {r.text}")
        break
        
    data = r.json()
    cards = data.get('cards', [])
    if not cards:
        break
        
    all_cards.extend(cards)
    print(f"Fetched {len(all_cards)} cards so far...")
    
    res_cursor = data.get('cursor', {})
    nm_id = res_cursor.get('nmID')
    updated_at = res_cursor.get('updatedAt')
    total = res_cursor.get('total', 0)
    
    if not nm_id or len(cards) < 100:
        break
        
    cursor['nmID'] = nm_id
    cursor['updatedAt'] = updated_at
    time.sleep(0.3)

with open('wb_cards_seo_dump.json', 'w', encoding='utf-8') as f:
    json.dump(all_cards, f, ensure_ascii=False, indent=2)

print(f"Saved {len(all_cards)} cards to wb_cards_seo_dump.json")
