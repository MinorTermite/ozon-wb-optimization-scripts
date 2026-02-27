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

def run_fix():
    if not os.path.exists(CANDIDATES_PATH) or not os.path.exists(DATA_DUMP_PATH):
        print("Required files missing")
        return

    with open(CANDIDATES_PATH, 'r', encoding='utf-8') as f:
        candidates = set(json.load(f))
    
    with open(DATA_DUMP_PATH, 'r', encoding='utf-8') as f:
        all_cards = json.load(f)
    
    target_data = [card for card in all_cards if card.get('nmID') in candidates]
    print(f"Final attempt: {len(target_data)} cards.")

    upload_url = 'https://content-api.wildberries.ru/content/v2/cards/upload'
    
    for i, card in enumerate(target_data):
        new_vendor_code = f"{card.get('vendorCode', '')}_v2"
        
        # Characteristics: Clean and ensure list of strings
        chars = []
        for c in card.get('characteristics', []):
            name = c.get('name')
            if name and name not in ['nmID', 'imtID', 'vendorCode', 'brand']:
                val = c.get('value', [])
                if not isinstance(val, list):
                    val = [str(val)]
                else:
                    val = [str(x) for x in val]
                chars.append({"name": name, "value": val})
        
        # Dimensions & Weight
        dims = card.get('dimensions', {})
        new_dimensions = {
            "width": max(1, int(dims.get('width', 10))),
            "height": max(1, int(dims.get('height', 2))),
            "length": max(1, int(dims.get('length', 15)))
        }
        
        # Photos
        media_files = []
        for p in card.get('photos', []):
            url = p.get('big') or p.get('hq')
            if url: media_files.append(url)

        # Sizes: Let WB generate barcodes by sending EMPTY SKUS for NEW cards
        new_sizes = []
        for s in card.get('sizes', []):
            new_sizes.append({
                "techSize": str(s.get('techSize', "0")),
                "wbSize": str(s.get('wbSize', "")),
                "skus": [] # This forces WB to generate new barcodes
            })

        upload_payload = [{
            "subjectID": card.get('subjectID'),
            "variants": [{
                "vendorCode": new_vendor_code,
                "brand": "GravMix",
                "title": card.get('title', '')[:50],
                "description": card.get('description', ''),
                "dimensions": new_dimensions,
                "characteristics": chars,
                "sizes": new_sizes,
                "mediaFiles": media_files
            }]
        }]
        
        print(f"[{i+1}/{len(target_data)}] Uploading {new_vendor_code}...")
        
        while True:
            response = requests.post(upload_url, headers=headers, json=upload_payload)
            if response.status_code == 200:
                print(f"Success: {new_vendor_code}")
                break
            elif response.status_code == 429:
                print("Rate limited. Waiting 60s...")
                time.sleep(60)
                continue
            else:
                print(f"Error {response.status_code}: {response.text}")
                break
        
        time.sleep(3) # Base throttle

if __name__ == "__main__":
    run_fix()
