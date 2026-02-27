import json
import os
import requests
import time

BASE_DIR = r'C:\Users\GravMix\.gemini\antigravity\playground\core-pulsar'
ENV_PATH = os.path.join(BASE_DIR, '.env')

# Load API key
WB_KEY = ''
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('WB_API_KEY='):
                WB_KEY = line.strip().split('=', 1)[1]
                break

if not WB_KEY:
    print("Error: WB_API_KEY not found")
    exit(1)

headers = {
    'Authorization': WB_KEY,
    'Content-Type': 'application/json'
}

def get_card_data(nm_id):
    url = 'https://content-api.wildberries.ru/content/v2/get/cards/list'
    payload = {
        "settings": {
            "cursor": {
                "limit": 10
            },
            "filter": {
                "nmID": int(nm_id),
                "withRoot": True
            }
        }
    }
    r = requests.post(url, headers=headers, json=payload)
    if r.status_code == 200:
        cards = r.json().get('cards', [])
        return cards[0] if cards else None
    return None

def clone_card(nm_id, new_vendor_code):
    card = get_card_data(nm_id)
    if not card:
        print(f"Error: Card {nm_id} not found.")
        return
    
    # Prepare payload for creation
    # WB Creation API: /content/v2/cards/upload
    # We need to adapt the structure
    
    payload = [{
        "subjectID": card.get('subjectID'),
        "variants": [{
            "vendorCode": new_vendor_code,
            "title": card.get('title'),
            "description": card.get('description'),
            "brand": "GravMix", # Force brand
            "dimensions": card.get('dimensions'),
            "characteristics": card.get('characteristics'),
            "sizes": [{
                "techSize": s.get('techSize'),
                "wbSize": s.get('wbSize'),
                "price": s.get('price'),
                "skus": [] # WB will generate new SKUs usually, or you can provide if allowed
            } for s in card.get('sizes', [])]
        }]
    }]
    
    url = 'https://content-api.wildberries.ru/content/v2/cards/upload'
    r = requests.post(url, headers=headers, json=payload)
    if r.status_code == 200:
        print(f"Successfully cloned card {nm_id} to new vendor code {new_vendor_code}.")
    else:
        print(f"Error cloning card: {r.status_code} {r.text}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python wb_clone_card.py <existing_nm_id> <new_vendor_code>")
        print("Example: python wb_clone_card.py 267766952 item_new_2026")
    else:
        clone_card(sys.argv[1], sys.argv[2])
