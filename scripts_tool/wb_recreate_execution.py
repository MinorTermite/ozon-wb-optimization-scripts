import json
import requests
import os
import time

BASE_DIR = r'C:\Users\GravMix\.gemini\antigravity\playground\core-pulsar'
ENV_PATH = os.path.join(BASE_DIR, '.env')
CANDIDATES_PATH = os.path.join(BASE_DIR, 'analytics', 'wb_recreate_nmids.json')
DATA_DUMP_PATH = os.path.join(BASE_DIR, 'data_dump', 'wb_cards_seo_dump.json')

WB_KEY = ''
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('WB_API_KEY='):
                WB_KEY = line.strip().split('=', 1)[1]
                break

headers = {'Authorization': WB_KEY, 'Content-Type': 'application/json'}

def recreate_cards():
    if not os.path.exists(CANDIDATES_PATH) or not os.path.exists(DATA_DUMP_PATH):
        print("Required files missing")
        return

    with open(CANDIDATES_PATH, 'r', encoding='utf-8') as f:
        candidates = set(json.load(f))
    
    with open(DATA_DUMP_PATH, 'r', encoding='utf-8') as f:
        all_cards = json.load(f)
    
    target_data = [card for card in all_cards if card.get('nmID') in candidates]
    print(f"Loaded {len(target_data)} cards for re-creation.")

    upload_url = 'https://content-api.wildberries.ru/content/v2/cards/upload'
    
    for i, card in enumerate(target_data):
        # Prepare the upload payload
        # Note: /content/v2/cards/upload expects a list of objects
        
        # We need to map the card fields to the upload format
        # Characteristics, vendorCode, sizes, media
        
        new_vendor_code = f"{card.get('vendorCode', '')}_v2"
        
        # Extract characteristics filtering out system ones like nmID
        chars = card.get('characteristics', [])
        
        # Prepare card object
        upload_obj = {
            "subjectID": card.get('subjectID'),
            "variants": [
                {
                    "vendorCode": new_vendor_code,
                    "brand": "GravMix",
                    "title": card.get('title', '')[:50], # Ensure SEO limit
                    "description": card.get('description', ''),
                    "characteristics": chars,
                    "sizes": card.get('sizes', []),
                    "mediaFiles": [m.get('url') for m in card.get('media', []) if m.get('url')]
                }
            ]
        }
        
        print(f"[{i+1}/{len(target_data)}] Uploading {new_vendor_code}...")
        
        response = requests.post(upload_url, headers=headers, json=[upload_obj])
        
        if response.status_code == 200:
            print(f"Success: {new_vendor_code}")
        elif response.status_code == 429:
            print("Rate limit hit. Sleeping 60s...")
            time.sleep(60)
            # Retry once
            response = requests.post(upload_url, headers=headers, json=[upload_obj])
            print(f"Retry status: {response.status_code}")
        else:
            print(f"Error {response.status_code}: {response.text}")
        
        # Throttle to avoid aggressive rate limiting
        time.sleep(2)

if __name__ == "__main__":
    recreate_cards()
