# -*- coding: utf-8 -*-
"""
WB SEO: find short descriptions and generate improved ones
"""
import json, re

with open('wb_cards_seo_dump.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

# Find the 22 short ones
short_cards = []
for c in cards:
    desc = c.get('description', '')
    if 0 < len(desc) < 500:
        short_cards.append({
            'nmID': c.get('nmID'),
            'title': c.get('title', ''),
            'desc_len': len(desc),
            'desc': desc,
            'vendorCode': c.get('vendorCode', '')
        })

print("Short description cards:", len(short_cards))
for i, sc in enumerate(short_cards):
    print(f"\n--- [{i+1}] nmID: {sc['nmID']} VC: {sc['vendorCode']} ---")
    print(f"Title: {sc['title']}")
    print(f"Desc ({sc['desc_len']} chars): {sc['desc'][:200]}...")

# Also check: what's the average for "good" cards for reference?
good_descs = [c for c in cards if 500 <= len(c.get('description', '')) <= 2000]
if good_descs:
    sample = good_descs[0]
    print("\n\n=== SAMPLE GOOD DESCRIPTION ===")
    print(f"Title: {sample.get('title')}")
    print(f"Desc ({len(sample.get('description',''))} chars):")
    print(sample.get('description', '')[:500])
