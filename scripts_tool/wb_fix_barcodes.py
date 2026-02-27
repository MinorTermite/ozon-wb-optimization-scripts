import json
import requests
import os
import time

BASE_DIR = r'C:\Users\GravMix\.gemini\antigravity\playground\core-pulsar'
ENV_PATH = os.path.join(BASE_DIR, '.env')
DATA_DUMP_PATH = os.path.join(BASE_DIR, 'data_dump', 'wb_cards_seo_dump.json')
CANDIDATES_PATH = os.path.join(BASE_DIR, 'analytics', 'wb_recreate_nmids.json')

WB_KEY = ''
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('WB_API_KEY='):
                WB_KEY = line.strip().split('=', 1)[1]
                break

headers = {'Authorization': WB_KEY, 'Content-Type': 'application/json'}

def fix_barcodes():
    if not os.path.exists(CANDIDATES_PATH) or not os.path.exists(DATA_DUMP_PATH):
        print("Required files missing")
        return

    with open(CANDIDATES_PATH, 'r', encoding='utf-8') as f:
        candidates = set(json.load(f))
    
    with open(DATA_DUMP_PATH, 'r', encoding='utf-8') as f:
        all_cards = json.load(f)
    
    target_data = [card for card in all_cards if card.get('nmID') in candidates]
    print(f"Fixing {len(target_data)} cards with barcode collisions.")

    upload_url = 'https://content-api.wildberries.ru/content/v2/cards/upload'
    
    for i, card in enumerate(target_data):
        new_vendor_code = f"{card.get('vendorCode', '')}_v2"
        
        # Clean characteristics
        chars = []
        for c in card.get('characteristics', []):
            if c.get('name') not in ['nmID', 'imtID']: # Skip internal IDs
                chars.append(c)
        
        # Clean and fix sizes (barcodes)
        new_sizes = []
        for s in card.get('sizes', []):
            # To generate a new unique barcode, we take the old one and add a 'V2' suffix or randomized part
            # Or better: let WB generate it by leaving skus empty? 
            # Actually, standard practice is providing a new one if possible. 
            # Let's try appending '2' or something.
            old_skus = s.get('skus', [])
            new_skus = []
            for b in old_skus:
                # Max barcode length is 20-30 chars, usually 13.
                new_b = f"{b}2" # Just append 2 to make it unique
                new_skus.append(new_b)
            
            new_sizes.append({
                "techSize": s.get('techSize'),
                "wbSize": s.get('wbSize'),
                "skus": new_skus # New unique barcodes
            })
        
        # Prepare card object
        upload_obj = {
            "subjectID": card.get('subjectID'),
            "variants": [
                {
                    "vendorCode": new_vendor_code,
                    "brand": "GravMix",
                    "title": card.get('title', '')[:50],
                    "description": card.get('description', ''),
                    "characteristics": chars,
                    "sizes": new_sizes,
                    "mediaFiles": [m.get('url') for m in card.get('media', []) if m.get('url')]
                }
            ]
        }
        
        print(f"[{i+1}/{len(target_data)}] Re-submitting {new_vendor_code} with new barcodes...")
        
        response = requests.post(upload_url, headers=headers, json=[upload_obj])
        
        if response.status_code == 200:
            print(f"Success: {new_vendor_code}")
        elif response.status_code == 429:
            print("Rate limit hit. Sleeping 60s...")
            time.sleep(60)
            response = requests.post(upload_url, headers=headers, json=[upload_obj])
            print(f"Retry status: {response.status_code}")
        else:
            print(f"Error {response.status_code}: {response.text}")
        
        time.sleep(2)

if __name__ == "__main__":
    fix_barcodes()
