import json
import os
import requests
import time

BASE_DIR = r'C:\Users\GravMix\.gemini\antigravity\playground\core-pulsar'
ANALYTICS_DIR = os.path.join(BASE_DIR, 'analytics')
CANDIDATES_PATH = os.path.join(ANALYTICS_DIR, 'wb_refresh_candidates.json')
ENV_PATH = os.path.join(BASE_DIR, '.env')

# Load API key
WB_KEY = ''
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('WB_API_KEY='):
                WB_KEY = line.strip().split('=', 1)
                if len(WB_KEY) == 2:
                    WB_KEY = WB_KEY[1].strip()
                break

if not WB_KEY:
    print("Error: WB_API_KEY not found")
    exit(1)

headers = {
    'Authorization': WB_KEY,
    'Content-Type': 'application/json'
}

# We will use the local dump which is known to be reliable
ALL_CARDS = []
DATA_DUMP_PATH = os.path.join(BASE_DIR, 'data_dump', 'wb_cards_seo_dump.json')

def fetch_catalog():
    global ALL_CARDS
    print(f"Loading catalog from {DATA_DUMP_PATH}...")
    if os.path.exists(DATA_DUMP_PATH):
        with open(DATA_DUMP_PATH, 'r', encoding='utf-8') as f:
            ALL_CARDS = json.load(f)
        print(f"Loaded {len(ALL_CARDS)} cards.")
    else:
        print("Error: Local dump not found.")

def get_card_full_details(nm_id):
    for card in ALL_CARDS:
        if card.get('nmID') == int(nm_id):
            return card
    return None

def archive_old_card(card):
    print(f"Archiving old card {card['nmID']}...")
    nm_id = card['nmID']
    # 1. Rename title
    update_url = 'https://content-api.wildberries.ru/content/v2/cards/update'
    
    # We strip any non-ASCII to be safe and cap at 60
    new_title = f"[АРХИВ] {card.get('title', '')}"[:60].strip()
    
    payload = [{
        "nmID": nm_id,
        "vendorCode": card.get('vendorCode'),
        "title": new_title,
        "description": card.get('description'),
        "characteristics": card.get('characteristics'),
        "dimensions": card.get('dimensions'),
        "sizes": card.get('sizes')
    }]
    
    # Push update
    r = requests.post(update_url, headers=headers, json=payload)
    if r.status_code == 200:
        print(f"Card {nm_id} renamed to [АРХИВ].")
    else:
        print(f"Error archiving title {nm_id}: {r.status_code} {r.text}")
        
    # Note: Setting stock to 0 is handled via Marketplace API, which requires SKU
    # For now, renaming and removing from visibility (by changing category if needed) is the standard 
    # but rename is most effective for SEO "deletion".

def execute_refresh():
    if not os.path.exists(CANDIDATES_PATH):
        print("No candidates found.")
        return
        
    with open(CANDIDATES_PATH, 'r', encoding='utf-8') as f:
        candidates = json.load(f)
        
    for cand in candidates:
        nm_id = cand['nmId']
        print(f"\nProcessing {nm_id} ({cand['name']})...")
        
        full_card = get_card_full_details(nm_id)
        if not full_card:
            print(f"Skipping {nm_id}, details not found.")
            continue
            
        # 1. Prepare New Card
        new_vendor_code = f"{full_card['vendorCode']}_v2"
        # Since we use /content/v2/cards/upload, it needs subjectID and variants
        upload_payload = [{
            "subjectID": full_card.get('subjectID'),
            "variants": [{
                "vendorCode": new_vendor_code,
                "title": full_card.get('title')[:60], # Ensure 60 char limit
                "description": full_card.get('description'),
                "brand": "GravMix",
                "dimensions": full_card.get('dimensions'),
                "characteristics": full_card.get('characteristics'),
                "sizes": [{
                    "techSize": s.get('techSize'),
                    "wbSize": s.get('wbSize'),
                    "price": s.get('price'),
                    "skus": [] # Let WB generate new ones
                } for s in full_card.get('sizes', [])]
            }]
        }]
        
        # 2. Upload New Card
        upload_url = 'https://content-api.wildberries.ru/content/v2/cards/upload'
        r = requests.post(upload_url, headers=headers, json=upload_payload)
        if r.status_code == 200:
            print(f"Successfully created version 2 for {nm_id} (Vendor: {new_vendor_code}).")
            # 3. Archive Old Card
            archive_old_card(full_card)
        else:
            print(f"Failed to clone {nm_id}: {r.status_code} {r.text}")
            
        time.sleep(5) # API safety

if __name__ == "__main__":
    fetch_catalog()
    execute_refresh()
