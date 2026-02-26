import json
import requests
import time

with open('.env', 'r', encoding='utf-8') as f:
    env = dict(line.strip().split('=', 1) for line in f if '=' in line and not line.startswith('#'))
H = {'Authorization': env['WB_API_KEY'], 'Content-Type': 'application/json'}

def investigate_wb():
    print("Loading WB cards dump...")
    try:
        with open('wb_cards_seo_dump.json', 'r', encoding='utf-8') as f:
            old_cards = json.load(f)
    except Exception as e:
        print(f"Error loading dump: {e}")
        return

    print(f"Total cards in dump: {len(old_cards)}")
    
    # Pick a few nmIDs to check
    nm_ids = [c['nmID'] for c in old_cards[:10]]
    print(f"Checking status for nmIDs: {nm_ids}")
    
    # Check current cards
    body = {"settings": {"cursor": {"limit": 100}, "filter": {"nmID": nm_ids}}}
    r = requests.post('https://content-api.wildberries.ru/content/v2/get/cards/list', headers=H, json=body)
    
    if r.status_code == 200:
        current_cards = r.json().get('data', {}).get('cards', [])
        print(f"Found {len(current_cards)} cards currently in API.")
        for c in current_cards:
            print(f"SKU: {c.get('vendorCode')}, Title: {c.get('title')}, nmID: {c.get('nmID')}")
    else:
        print(f"Error fetching current cards: {r.status_code} {r.text}")

    # Also check if they are in error list
    print("\nChecking for card errors...")
    r_err = requests.post('https://content-api.wildberries.ru/content/v2/cards/error/list', headers=H, json={'locale':'ru'})
    if r_err.status_code == 200:
        err_data = r_err.json().get('data', [])
        print(f"Total entries in error list: {len(err_data)}")
        for e in err_data:
            print(f"Error Entry: {e}")
    else:
        print(f"Error fetching error list: {r_err.status_code}")

if __name__ == "__main__":
    investigate_wb()
