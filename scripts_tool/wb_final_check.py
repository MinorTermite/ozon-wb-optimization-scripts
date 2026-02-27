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

def check_vendors():
    url = 'https://content-api.wildberries.ru/content/v2/get/cards/list'
    # Use one of the vendor codes that was in the error list earlier
    target_vendors = ["wb5i9ylyy4g", "wb21i9v4z4", "wbnpjaxo0"]
    
    print(f"Searching for vendors: {target_vendors}")
    payload = {
        "settings": {
            "cursor": { "limit": 100 },
            "filter": { 
                "withRoot": False
                # V2 API filter by vendorCode is often not supported in body, but let's try 
                # or just fetch everything and find locally.
            }
        }
    }
    # Wait, if cards/list only returns 4, then searching won't help unless I find a DIFFERENT endpoint.
    
    # Let's try /content/v2/get/cards/list with NO cursor total limit?
    # Or maybe the 174 drafts are in a "Pending" state that is NOT listable yet.
    
    # Actually, I'll check the Error List ONE last time.
    err_url = 'https://content-api.wildberries.ru/content/v2/cards/error/list'
    r = requests.post(err_url, headers=headers, json={"settings":{"cursor":{"limit":100}}})
    print(f"Final Error List Count: {len(r.json().get('data', {}).get('cards', []))}")

if __name__ == "__main__":
    check_vendors()
