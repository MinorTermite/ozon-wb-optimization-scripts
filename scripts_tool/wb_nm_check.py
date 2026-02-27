import json
import requests
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

def check_specific_nm(nm_id):
    url = 'https://content-api.wildberries.ru/content/v2/get/cards/list'
    # Wildberries V2 doesn't have a direct "filter by nmID" in cards/list payload usually, 
    # but we can try to find it via specific filters or just check error list/trash.
    # Actually, let's try to fetch errors (POST!) again but more carefully.
    
    print(f"Checking for NM {nm_id} in error list...")
    err_url = 'https://content-api.wildberries.ru/content/v2/cards/error/list'
    payload = {
        "settings": {
            "cursor": { "limit": 100 }
        }
    }
    r = requests.post(err_url, headers=headers, json=payload)
    if r.status_code == 200:
        data = r.json()
        print("Error list response successful.")
        with open('error_list_full.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    else:
        print(f"Error fetching error list: {r.status_code} {r.text}")

if __name__ == "__main__":
    check_specific_nm(345800844) # One of the old nmIDs
