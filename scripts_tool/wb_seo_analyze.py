# -*- coding: utf-8 -*-
"""
Analyze WB cards for SEO metrics
"""
import os, json, re
from collections import Counter

# Process data
with open('wb_cards_seo_dump.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

print(f"Total cards loaded: {len(cards)}")

seo_stats = {
    'no_description': 0,
    'short_description_under_500': 0,
    'good_description_500_2000': 0,
    'long_description_over_2000': 0,
    'missing_characteristics': 0,
    'total_chars': 0
}

wordsCount = Counter()

bad_examples = []
good_examples = []

for c in cards:
    desc = c.get('description', '')
    desc_len = len(desc)
    title = c.get('title', '')
    nmID = c.get('nmID', '')
    
    seo_stats['total_chars'] += desc_len
    
    if desc_len == 0:
        seo_stats['no_description'] += 1
        bad_examples.append(f"NO DESC: {title} (nmID: {nmID})")
    elif desc_len < 500:
        seo_stats['short_description_under_500'] += 1
        if len(bad_examples) < 5:
             bad_examples.append(f"SHORT ({desc_len}ch): {title} (nmID: {nmID})")
    elif desc_len > 2000:
        seo_stats['long_description_over_2000'] += 1
        if len(good_examples) < 5:
             good_examples.append(f"LONG ({desc_len}ch): {title} (nmID: {nmID})")
    else:
        seo_stats['good_description_500_2000'] += 1
        
    chars = c.get('characteristics', [])
    if len(chars) < 5:
        seo_stats['missing_characteristics'] += 1
        
    words = re.findall(r'[а-яА-Яa-zA-Z]{4,}', desc.lower())
    wordsCount.update(words)

print("\n--- SEO METRICS SUMMARY ---")
print(f"Total Cards Analyzed: {len(cards)}")
print(f"No description: {seo_stats['no_description']}")
print(f"Short desc (<500): {seo_stats['short_description_under_500']} (Needs expansion!)")
print(f"Good desc (500-2000): {seo_stats['good_description_500_2000']}")
print(f"Long desc (>2000): {seo_stats['long_description_over_2000']}")
print(f"Cards with <5 characteristics: {seo_stats['missing_characteristics']}")
print(f"Average desc length: {seo_stats['total_chars'] / len(cards) if cards else 0:.0f} chars")

print("\n--- TOP 15 KEYWORDS ---")
for w, c in wordsCount.most_common(15):
    print(f"  {w}: {c}")

print("\n--- ISSUE EXAMPLES ---")
for ex in bad_examples[:5]:
    print(f"  {ex}")
