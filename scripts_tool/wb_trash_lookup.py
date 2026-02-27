import requests
import json
import os

BASE_DIR = r'C:\Users\GravMix\.gemini\antigravity\playground\core-pulsar'
ENV_PATH = os.path.join(BASE_DIR, '.env')
DATA_DUMP_PATH = os.path.join(BASE_DIR, 'data_dump', 'wb_cards_seo_dump.json')

WB_KEY = ''
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('WB_API_KEY='):
                WB_KEY = line.strip().split('=', 1)[1]
                break

headers = {'Authorization': WB_KEY, 'Content-Type': 'application/json'}

def check_trash_targeted():
    if not os.path.exists(DATA_DUMP_PATH):
        print("Historical dump missing")
        return

    with open(DATA_DUMP_PATH, 'r', encoding='utf-8') as f:
        cards = json.load(f)
    
    # nmIDs that are missing from the main list
    nmids = [c.get('nmID') for c in cards[:20] if c.get('nmID')]
    print(f"Checking if {len(nmids)} missing nmIDs are in Trash...")
    
    url = 'https://content-api.wildberries.ru/content/v2/get/cards/trash'
    payload = {
        "settings": {
            "cursor": { "limit": 100 },
            "filter": { "nmID": nmids }
        }
    }
    r = requests.post(url, headers=headers, json=payload)
    if r.status_code == 200:
        found = r.json().get('cards', [])
        print(f"Found {len(found)} items in Trash.")
        for f_card in found:
            print(f"- Trash ID: {f_card.get('nmID')} ({f_card.get('vendorCode')})")
    else:
        print(f"Error {r.status_code}: {r.text}")

if __name__ == "__main__":
    check_trash_targeted()
