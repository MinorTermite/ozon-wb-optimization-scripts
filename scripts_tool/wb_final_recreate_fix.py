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

def fix_everything():
    if not os.path.exists(CANDIDATES_PATH) or not os.path.exists(DATA_DUMP_PATH):
        print("Required files missing")
        return

    with open(CANDIDATES_PATH, 'r', encoding='utf-8') as f:
        candidates = set(json.load(f))
    
    with open(DATA_DUMP_PATH, 'r', encoding='utf-8') as f:
        all_cards = json.load(f)
    
    target_data = [card for card in all_cards if card.get('nmID') in candidates]
    print(f"Fixing {len(target_data)} cards with full migration (Dimensions, Photos, Barcodes).")

    upload_url = 'https://content-api.wildberries.ru/content/v2/cards/upload'
    
    for i, card in enumerate(target_data):
        new_vendor_code = f"{card.get('vendorCode', '')}_v2"
        
        # 1. Clean characteristics
        chars = []
        for c in card.get('characteristics', []):
            if c.get('name') not in ['nmID', 'imtID']:
                chars.append(c)
        
        # 2. Extract Dimensions & Weight
        dims = card.get('dimensions', {})
        new_dimensions = {
            "width": dims.get('width', 10),
            "height": dims.get('height', 2),
            "length": dims.get('length', 15)
        }
        
        # Weight often needs to be in characteristics too if not in dimensions V2
        # Let's see if 14177450 (Weight with packaging) is there
        has_weight = any(c.get('id') == 14177450 or c.get('name') == "Вес с упаковкой (кг)" for c in chars)
        if not has_weight and dims.get('weightBrutto'):
            chars.append({
                "name": "Вес с упаковкой (кг)",
                "value": [str(dims.get('weightBrutto'))]
            })

        # 3. Fix sizes & Barcodes
        new_sizes = []
        for s in card.get('sizes', []):
            old_skus = s.get('skus', [])
            new_skus = [f"{b}2" for b in old_skus] if old_skus else []
            
            new_sizes.append({
                "techSize": s.get('techSize', "0"),
                "wbSize": s.get('wbSize', ""),
                "skus": new_skus
            })
        
        # 4. Correct Media Files (Photos)
        # The dump uses 'photos' with 'big' key
        media_files = []
        for p in card.get('photos', []):
            url = p.get('big') or p.get('hq')
            if url:
                media_files.append(url)

        # Prepare card object
        upload_obj = {
            "subjectID": card.get('subjectID'),
            "variants": [
                {
                    "vendorCode": new_vendor_code,
                    "brand": "GravMix",
                    "title": card.get('title', '')[:50],
                    "description": card.get('description', ''),
                    "dimensions": new_dimensions,
                    "characteristics": chars,
                    "sizes": new_sizes,
                    "mediaFiles": media_files
                }
            ]
        }
        
        print(f"[{i+1}/{len(target_data)}] Final Resubmission: {new_vendor_code}...")
        
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
    fix_everything()
