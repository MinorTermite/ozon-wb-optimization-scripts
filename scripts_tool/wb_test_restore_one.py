# -*- coding: utf-8 -*-
import json, requests

with open('.env', 'r', encoding='utf-8') as f:
    env = dict(line.strip().split('=', 1) for line in f if '=' in line and not line.startswith('#'))

WB_KEY = env['WB_API_KEY']
H = {'Authorization': WB_KEY, 'Content-Type': 'application/json'}

with open('wb_cards_seo_dump.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

# Find "12345zodiakCancer"
target_vc = "12345zodiakCancer"
card = next((c for c in cards if c['vendorCode'] == target_vc), None)

if not card:
    print("Card not found!")
    exit(1)

# Apply fixes
sid = card.get('subjectID')
new_chars = []
for ch in card.get('characteristics', []):
    # Just mock some fixes for the test
    if ch.get('name') in ['Ширина предмета', 'Высота предмета', 'Длина предмета', 'Количество предметов в упаковке']:
        val = ch.get('value', [])
        new_val = []
        for v in val:
            try:
                new_val.append(int(float(v)))
            except:
                new_val.append(v)
        new_chars.append({'id': ch['id'], 'name': ch['name'], 'value': new_val})
    else:
        new_chars.append(ch)

body = [{
    "nmID": card['nmID'],
    "vendorCode": card['vendorCode'],
    "title": card['title'] + " GRAVMIX",
    "description": card['description'],
    "sizes": card.get('sizes', []),
    "characteristics": new_chars,
    "dimensions": {
        "width": 5,
        "height": 2,
        "length": 5,
        "weightBrutto": 0.05,
        "isValid": True
    }
}]

print(f"Testing fix on {target_vc}...")
r = requests.post('https://content-api.wildberries.ru/content/v2/cards/update', headers=H, json=body, timeout=15)
print(f"Status: {r.status_code}")
print(f"Response: {r.text}")
