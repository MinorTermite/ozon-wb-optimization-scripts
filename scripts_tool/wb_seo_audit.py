# -*- coding: utf-8 -*-
"""
WB Content API: Fetch all cards for SEO Audit
"""
import os, json, requests

env_path = '.env'
WB_KEY = ''
with open(env_path, 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('WB_API_KEY='):
            WB_KEY = line.strip().split('=', 1)[1]
            break

H = {'Authorization': WB_KEY, 'Content-Type': 'application/json'}

print("Fetching all WB cards for SEO analysis...")
cards = []
limit = 100
updated_at = ""
nm_id = 0

while True:
    payload = {
        "settings": {
            "cursor": {
                "limit": limit
            },
            "filter": {
                "withPhoto": -1
            }
        }
    }
    
    if updated_at:
        payload["settings"]["cursor"]["updatedAt"] = updated_at
        payload["settings"]["cursor"]["nmID"] = nm_id
        
    r = requests.post('https://content-api.wildberries.ru/content/v2/get/cards/list', headers=H, json=payload, timeout=30)
    
    if r.status_code == 200:
        data = r.json()
        batch = data.get('cards', [])
        
        if not batch:
            break
            
        cards.extend(batch)
        print(f"Fetched {len(batch)} cards... (Total: {len(cards)})")
        
        cursor = data.get('cursor', {})
        updated_at = cursor.get('updatedAt')
        nm_id = cursor.get('nmID')
        
        if not updated_at or len(batch) < limit:
            break
    else:
        print(f"ERROR: {r.status_code} {r.text[:200]}")
        break

print(f"\nTotal cards fetched: {len(cards)}")

# Save raw dump for analysis
with open("wb_cards_seo_dump.json", "w", encoding="utf-8") as f:
    json.dump(cards, f, ensure_ascii=False, indent=2)

print("Saved raw data to wb_cards_seo_dump.json")

# Process for SEO metrics
print("\n--- SEO METRICS SUMMARY ---")
seo_stats = {
    "no_description": 0,
    "short_description_under_500": 0,
    "good_description_500_2000": 0,
    "long_description_over_2000": 0,
    "missing_characteristics": 0,
    "total_chars": 0
}

# Example analysis on first 5
for i, c in enumerate(cards):
    desc = c.get('description', '')
    desc_len = len(desc)
    seo_stats["total_chars"] += desc_len
    
    if desc_len == 0:
        seo_stats["no_description"] += 1
    elif desc_len < 500:
        seo_stats["short_description_under_500"] += 1
    elif desc_len > 2000:
        seo_stats["long_description_over_2000"] += 1
    else:
        seo_stats["good_description_500_2000"] += 1
        
    # check characteristics
    chars = c.get('characteristics', [])
    if len(chars) < 5:
        seo_stats["missing_characteristics"] += 1

print(f"Total Cards analyzed: {len(cards)}")
print(f"No description: {seo_stats['no_description']}")
print(f"Short desc (<500): {seo_stats['short_description_under_500']} (Needs expansion!)")
print(f"Good desc (500-2000): {seo_stats['good_description_500_2000']}")
print(f"Long desc (>2000): {seo_stats['long_description_over_2000']}")
print(f"Cards with <5 characteristics: {seo_stats['missing_characteristics']}")
print(f"Average desc length: {seo_stats['total_chars'] / len(cards) if cards else 0:.0f} chars")

if cards:
    print("\nExample Card Structure:")
    c0 = cards[0]
    print(f"Title: {c0.get('title')}")
    print(f"Desc: {c0.get('description', '')[:100]}...")
    print(f"Characteristics count: {len(c0.get('characteristics', []))}")
    print(f"Colors/Sizes structure: {json.dumps(c0.get('sizes', []), ensure_ascii=False)[:200]}")
