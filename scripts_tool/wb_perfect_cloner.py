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

def perfect_clone():
    if not os.path.exists(CANDIDATES_PATH) or not os.path.exists(DATA_DUMP_PATH):
        print("Required files missing")
        return

    with open(CANDIDATES_PATH, 'r', encoding='utf-8') as f:
        candidates = set(json.load(f))
    
    with open(DATA_DUMP_PATH, 'r', encoding='utf-8') as f:
        all_cards = json.load(f)
    
    target_data = [card for card in all_cards if card.get('nmID') in candidates]
    print(f"Perfect Cloner: Starting for {len(target_data)} cards.")

    upload_url = 'https://content-api.wildberries.ru/content/v2/cards/upload'
    
    for i, card in enumerate(target_data):
        # Using a consistent suffix _CLONED
        new_vendor_code = f"{card.get('vendorCode', '')}_CLONED"
        
        # 1. Exhaustive copy of characteristics
        chars = []
        for c in card.get('characteristics', []):
            name = c.get('name')
            # Pass everything except IDs which are volatile
            if name and name not in ['nmID', 'imtID', 'vendorCode', 'brand']:
                val = c.get('value', [])
                if not isinstance(val, list): val = [str(val)]
                else: val = [str(x) for x in val]
                chars.append({"name": name, "value": val})
        
        # 2. Dimensions & Weight
        dims = card.get('dimensions', {})
        # WeightBrutto must be > 0 in V2 UI for it to be valid
        weight = dims.get('weightBrutto') or 100
        if weight == 0: weight = 100 # 100g as safe default
        
        # Some subjects use "Вес товара с упаковкой (г)" as a characteristic ID 14177450
        # If it's missing, we add it.
        has_weight = any("Вес" in c.get('name', '') for c in chars)
        if not has_weight:
            chars.append({"name": "Вес товара с упаковкой (г)", "value": [str(int(weight*1000) if weight < 1 else int(weight))]})
            # Wait, if weight is 0.15, we want 150g or just "0.15" depending on units.
            # Jewelry usually uses Kg in characteristics or Grams. 
            # In Step 1226 it was weightBrutto: 0.15.
        
        # 3. MediaFiles (Initial attempt)
        media_files = []
        for p in card.get('photos', []):
            url = p.get('big') or p.get('hq')
            if url: media_files.append(url)

        # 4. Payload for Upload
        payload = [{
            "subjectID": card.get('subjectID'),
            "variants": [{
                "vendorCode": new_vendor_code,
                "brand": "GravMix",
                "title": card.get('title', '')[:50],
                "description": card.get('description', ''),
                "dimensions": {
                    "width": max(1, int(dims.get('width', 10))),
                    "height": max(1, int(dims.get('height', 2))),
                    "length": max(1, int(dims.get('length', 15)))
                },
                "characteristics": chars,
                "sizes": [{
                    "techSize": str(s.get('techSize', "0")),
                    "wbSize": str(s.get('wbSize', "")),
                    "skus": [] # Generate unique barcodes
                } for s in card.get('sizes', [])],
                "mediaFiles": media_files
            }]
        }]
        
        print(f"[{i+1}/{len(target_data)}] Cloning {new_vendor_code}...")
        
        max_retries = 3
        for attempt in range(max_retries):
            response = requests.post(upload_url, headers=headers, json=payload)
            if response.status_code == 200:
                print(f"Success: {new_vendor_code}")
                break
            elif response.status_code == 429:
                print("Rate limited. Waiting 60s...")
                time.sleep(60)
            else:
                print(f"Error {response.status_code}: {response.text}")
                break
        
        time.sleep(3) # Base throttle

if __name__ == "__main__":
    perfect_clone()
