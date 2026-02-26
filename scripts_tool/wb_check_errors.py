# -*- coding: utf-8 -*-
"""
WB: Re-download ALL cards (including drafts/errors) and find issues
"""
import requests, json, time

with open('.env', 'r', encoding='utf-8') as f:
    env = {}
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k] = v

WB_KEY = env['WB_API_KEY']
H = {'Authorization': WB_KEY, 'Content-Type': 'application/json'}

# Fetch error list first (cards that need fixes)
print("=== CHECKING ERROR LIST ===")
r_err = requests.post('https://content-api.wildberries.ru/content/v2/cards/error/list', headers=H, json={"limit": 100}, timeout=15)
if r_err.status_code == 200:
    data = r_err.json()
    err_cards = data.get('data', [])
    print(f"Cards with errors: {len(err_cards)}")
    for ec in err_cards[:10]:
        nmID = ec.get('nmID', ec.get('id', 'N/A'))
        vc = ec.get('vendorCode', 'N/A')
        errors = ec.get('errors', [])
        print(f"  [{vc}] nmID:{nmID}")
        for e in errors[:3]:
            print(f"    - {e}")
    if len(err_cards) > 10:
        print(f"  ... and {len(err_cards) - 10} more")
else:
    print(f"Error list API: {r_err.status_code} {r_err.text[:200]}")

# Also check drafts/moderation
print("\n=== RE-DOWNLOADING ALL CARDS ===")
all_cards = []
cursor = {"limit": 100, "updatedAt": "", "nmID": 0}
total = 0
while True:
    body = {"settings": {"cursor": cursor, "filter": {"withPhoto": -1}}}
    r = requests.post('https://content-api.wildberries.ru/content/v2/get/cards/list', headers=H, json=body, timeout=30)
    if r.status_code != 200:
        print(f"Fetch error: {r.status_code} {r.text[:100]}")
        break
    data = r.json().get('data', {})
    cards_batch = data.get('cards', [])
    if not cards_batch:
        break
    all_cards.extend(cards_batch)
    total += len(cards_batch)
    cur = data.get('cursor', {})
    cursor['updatedAt'] = cur.get('updatedAt', '')
    cursor['nmID'] = cur.get('nmID', 0)
    time.sleep(0.5)

print(f"Total cards re-downloaded: {total}")

# Save fresh data
with open('wb_cards_fresh.json', 'w', encoding='utf-8') as f:
    json.dump(all_cards, f, ensure_ascii=False, indent=2)

# Quick analysis of fresh data
print("\n=== FRESH DATA ANALYSIS ===")
short_desc = sum(1 for c in all_cards if len(c.get('description', '')) < 500)
short_title = sum(1 for c in all_cards if len(c.get('title', '')) < 30)
no_dims = sum(1 for c in all_cards if not c.get('dimensions', {}).get('isValid', False))
print(f"Short descriptions: {short_desc}")
print(f"Short titles: {short_title}")
print(f"Invalid dimensions: {no_dims}")
