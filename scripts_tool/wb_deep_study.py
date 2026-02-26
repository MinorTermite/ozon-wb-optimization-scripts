# -*- coding: utf-8 -*-
"""
Deep analysis of WB card structure - study ALL fields and characteristics
"""
import json

with open('wb_cards_seo_dump.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

# Study one card in full detail
c = cards[0]
print("=== FULL CARD STRUCTURE ===")
print(f"Keys: {list(c.keys())}")
print()

for key in c.keys():
    val = c[key]
    if isinstance(val, str):
        print(f"[{key}] (string, {len(val)} chars): {val[:100]}")
    elif isinstance(val, (int, float)):
        print(f"[{key}] (number): {val}")
    elif isinstance(val, list):
        print(f"[{key}] (list, {len(val)} items):")
        if val:
            if isinstance(val[0], dict):
                print(f"  First item keys: {list(val[0].keys())}")
                print(f"  First item: {json.dumps(val[0], ensure_ascii=False)[:150]}")
            else:
                print(f"  First items: {val[:3]}")
    elif isinstance(val, dict):
        print(f"[{key}] (dict): {json.dumps(val, ensure_ascii=False)[:150]}")
    else:
        print(f"[{key}] ({type(val).__name__}): {val}")

# Study characteristics structure
print("\n\n=== CHARACTERISTICS (all fields in card) ===")
chars = c.get('characteristics', [])
print(f"Total characteristics: {len(chars)}")
for ch in chars:
    print(f"  {json.dumps(ch, ensure_ascii=False)[:120]}")

# Study sizes structure
print("\n\n=== SIZES ===")
sizes = c.get('sizes', [])
print(f"Total sizes: {len(sizes)}")
for s in sizes:
    print(f"  {json.dumps(s, ensure_ascii=False)[:150]}")

# Study photos structure
print("\n\n=== PHOTOS ===")
photos = c.get('photos', [])
print(f"Total photos: {len(photos)}")
if photos:
    print(f"  First photo: {json.dumps(photos[0], ensure_ascii=False)[:200]}")

# Study dimensions
print("\n\n=== DIMENSIONS ===")
dims = c.get('dimensions', {})
print(f"  {json.dumps(dims, ensure_ascii=False)}")

# Find what subjectIDs exist in our catalog
print("\n\n=== SUBJECT IDs ===")
subjects = {}
for c2 in cards:
    sid = c2.get('subjectID')
    sname = c2.get('subjectName', '')
    if sid not in subjects:
        subjects[sid] = {'name': sname, 'count': 0}
    subjects[sid]['count'] += 1

for sid, info in sorted(subjects.items(), key=lambda x: -x[1]['count']):
    print(f"  [{sid}] {info['name']}: {info['count']} cards")

# Study what characteristics are MOST COMMON per subject
print("\n\n=== CHARACTERISTICS BY SUBJECT ===")
for sid, info in sorted(subjects.items(), key=lambda x: -x[1]['count']):
    subject_cards = [c2 for c2 in cards if c2.get('subjectID') == sid]
    char_freq = {}
    for sc in subject_cards:
        for ch in sc.get('characteristics', []):
            name = ch.get('name', ch.get('id', 'unknown'))
            char_freq[name] = char_freq.get(name, 0) + 1
    
    print(f"\n  [{sid}] {info['name']} ({info['count']} cards):")
    for cn, cnt in sorted(char_freq.items(), key=lambda x: -x[1]):
        pct = cnt / info['count'] * 100
        marker = " <<<" if pct < 100 else ""
        print(f"    {cn}: {cnt}/{info['count']} ({pct:.0f}%){marker}")
