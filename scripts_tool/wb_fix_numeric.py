# -*- coding: utf-8 -*-
"""
WB Fix: numeric characteristics (Ширина/Высота/Длина предмета)
Must be sent as numeric values, not strings
Also fixes dimensions (packaging size: 5x5x2 cm)
"""
import json, requests, time

with open('.env', 'r', encoding='utf-8') as f:
    env = {}
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k] = v

WB_KEY = env['WB_API_KEY']
H = {'Authorization': WB_KEY, 'Content-Type': 'application/json'}

with open('wb_cards_seo_dump.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

# Find cards that have string values for numeric characteristics
# or are missing dimensions
NUMERIC_CHARS = {'Ширина предмета', 'Высота предмета', 'Длина предмета', 'Количество предметов в упаковке'}

updates = []
for c in cards:
    nmID = c['nmID']
    vc = c['vendorCode']
    sizes = c.get('sizes', [])
    chars = list(c.get('characteristics', []))
    dims = c.get('dimensions', {})
    needs_update = False
    
    # Fix numeric characteristics: ensure values are proper format
    new_chars = []
    for ch in chars:
        name = ch.get('name', '')
        if name in NUMERIC_CHARS:
            val = ch.get('value', [])
            # Convert string values to proper format
            if val and isinstance(val[0], str):
                try:
                    numeric_val = int(float(val[0]))
                    new_chars.append({'id': ch['id'], 'name': name, 'value': [str(numeric_val)]})
                    needs_update = True
                    continue
                except (ValueError, TypeError):
                    pass
        new_chars.append(ch)
    
    # Fix dimensions if wrong
    if not dims.get('isValid', True) or dims.get('width', 0) == 0:
        needs_update = True
    
    if needs_update:
        update = {
            "nmID": nmID,
            "vendorCode": vc,
            "sizes": sizes,
            "characteristics": new_chars,
            "dimensions": {
                "width": 5,
                "height": 2,
                "length": 5
            }
        }
        updates.append({'body': update, 'vc': vc})

print(f"Cards needing numeric fix: {len(updates)}")

# Apply
ok = 0
err = 0
for i, u in enumerate(updates):
    body = [u['body']]
    try:
        r = requests.post('https://content-api.wildberries.ru/content/v2/cards/update', headers=H, json=body, timeout=15)
        if r.status_code == 200 and not r.json().get('error'):
            ok += 1
        elif r.status_code == 429:
            time.sleep(10)
            r2 = requests.post('https://content-api.wildberries.ru/content/v2/cards/update', headers=H, json=body, timeout=15)
            if r2.status_code == 200 and not r2.json().get('error'):
                ok += 1
            else:
                err += 1
                print(f"  ERR (retry) [{u['vc']}]: {r2.status_code} {r2.text[:100]}")
        else:
            err += 1
            if err <= 5:
                print(f"  ERR [{u['vc']}]: {r.status_code} {r.text[:100]}")
    except Exception as e:
        err += 1
    
    if (i + 1) % 10 == 0:
        print(f"  progress: {i+1}/{len(updates)} ok:{ok} err:{err}")
    time.sleep(3)

print(f"\nDONE: {ok} fixed, {err} errors")
