# -*- coding: utf-8 -*-
import json, re

with open("wb_cards_seo_dump.json", "r", encoding="utf-8") as f:
    cards = json.load(f)

stats = {
    "total": len(cards),
    "no_desc": 0,
    "short": 0,
    "good": 0,
    "long": 0,
    "missing_chars": 0,
    "total_chars": 0
}

bad = []

for c in cards:
    desc = c.get('description', '')
    desc_len = len(desc)
    title = c.get('title', '')
    
    stats["total_chars"] += desc_len
    
    if desc_len == 0:
        stats["no_desc"] += 1
        bad.append(f"EMPTY: {title}")
    elif desc_len < 500:
        stats["short"] += 1
        bad.append(f"SHORT ({desc_len}): {title}")
    elif desc_len > 2000:
        stats["long"] += 1
    else:
        stats["good"] += 1
        
    chars = c.get('characteristics', [])
    if len(chars) < 5:
        stats["missing_chars"] += 1

out = []
out.append(f"Total: {stats['total']}")
out.append(f"No DESC: {stats['no_desc']}")
out.append(f"Short (<500): {stats['short']}")
out.append(f"Good (500-2000): {stats['good']}")
out.append(f"Long (>2000): {stats['long']}")
out.append(f"Missing Chars (<5): {stats['missing_chars']}")
out.append(f"Avg length: {stats['total_chars'] / max(1, stats['total']):.0f}")

out.append("\nISSUES:")
for b in bad[:10]:
    out.append(f" - {b}")

with open("wb_seo_report_text.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print("DONE")
