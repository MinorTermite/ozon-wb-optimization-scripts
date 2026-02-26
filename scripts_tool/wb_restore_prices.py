import json
import requests
import time

with open('.env', 'r', encoding='utf-8') as f:
    env = dict(line.strip().split('=', 1) for line in f if '=' in line and not line.startswith('#'))
H = {'Authorization': env['WB_API_KEY'], 'Content-Type': 'application/json'}

def restore_wb_prices():
    print("Loading WB cards dump...")
    try:
        with open('wb_cards_seo_dump.json', 'r', encoding='utf-8') as f:
            cards = json.load(f)
    except Exception as e:
        print(f"Error loading dump: {e}")
        return

    print(f"Loaded {len(cards)} cards from dump. Restoring price to 1548 RUB...")

    updates = []
    for c in cards:
        # Prepare the update object exactly like in wb_deep_seo.py but with correct price
        # Note: we need to maintain all fields for v2/cards/update to be safe
        
        # We reuse the logic from wb_deep_seo.py but with price 1548
        # (Assuming the original titles/descs were already updated by the previous script)
        # Actually, let's just use the current state from the dump and fix the price.
        
        # First, ensure characteristics are in the right format (WB API is picky)
        clean_chars = []
        for ch in c.get('characteristics', []):
            clean_chars.append({"id": ch['id'], "name": ch['name'], "value": ch['value']})

        u = {
            "nmID": c['nmID'],
            "imtID": c['imtID'],
            "vendorCode": c['vendorCode'],
            "title": c.get('title', ''),
            "description": c.get('description', ''),
            "characteristics": clean_chars,
            "sizes": [
                {
                    "chrtID": c['sizes'][0]['chrtID'],
                    "wbSize": c['sizes'][0].get('wbSize', ''), 
                    "price": 1548, # RESTORE PRICE
                    "skus": c['sizes'][0].get('skus', [])
                }
            ],
            "dimensions": { "length": 15, "width": 10, "height": 3, "weightBrutto": 0.15, "isValid": True }
        }
        updates.append(u)

    print(f"Sending price restoration for {len(updates)} cards...")
    BATCH_SIZE = 50
    ok, err = 0, 0
    for i in range(0, len(updates), BATCH_SIZE):
        batch = updates[i:i+BATCH_SIZE]
        r = requests.post('https://content-api.wildberries.ru/content/v2/cards/update', headers=H, json=batch)
        if r.status_code == 200:
            ok += len(batch)
            print(f"  Batch {i//BATCH_SIZE + 1} Success. ({ok}/{len(updates)})")
        else:
            err += len(batch)
            print(f"  Batch {i//BATCH_SIZE + 1} Error: {r.status_code} {r.text[:200]}")
        time.sleep(3)

    print(f"\nWB PRICE RESTORATION FINISHED: {ok} OK, {err} ERR")

if __name__ == "__main__":
    restore_wb_prices()
