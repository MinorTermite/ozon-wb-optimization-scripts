# -*- coding: utf-8 -*-
"""
WB Full Cabinet Audit — comprehensive analysis of all 266 cards
Checks: descriptions, characteristics, photos, titles, SEO keywords
"""
import json, re, os

with open('wb_cards_seo_dump.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

print(f"=== WB FULL AUDIT: {len(cards)} cards ===\n")

# Counters
issues = {
    'no_desc': [], 'short_desc': [], 'long_desc': [],
    'no_photos': [], 'few_photos': [],
    'short_title': [], 'long_title': [],
    'few_chars': [], 'missing_brand': [],
    'no_dimensions': [], 'no_composition': [],
    'duplicate_titles': {},
}

total_desc_len = 0
total_photo_count = 0
total_char_count = 0
char_names_all = {}

for c in cards:
    nmID = c.get('nmID', 0)
    title = c.get('title', '')
    desc = c.get('description', '')
    photos = c.get('photos', [])
    chars = c.get('characteristics', [])
    brand = c.get('brand', '')
    vc = c.get('vendorCode', '')
    
    dlen = len(desc)
    total_desc_len += dlen
    total_photo_count += len(photos)
    total_char_count += len(chars)
    
    # Track characteristic names
    for ch in chars:
        for key in ch:
            char_names_all[key] = char_names_all.get(key, 0) + 1
    
    # Description checks
    if dlen == 0:
        issues['no_desc'].append({'nmID': nmID, 'vc': vc, 'title': title[:50]})
    elif dlen < 500:
        issues['short_desc'].append({'nmID': nmID, 'vc': vc, 'title': title[:50], 'len': dlen})
    elif dlen > 2000:
        issues['long_desc'].append({'nmID': nmID, 'vc': vc, 'title': title[:50], 'len': dlen})
    
    # Photo checks
    if len(photos) == 0:
        issues['no_photos'].append({'nmID': nmID, 'vc': vc, 'title': title[:50]})
    elif len(photos) < 3:
        issues['few_photos'].append({'nmID': nmID, 'vc': vc, 'title': title[:50], 'count': len(photos)})
    
    # Title checks
    if len(title) < 30:
        issues['short_title'].append({'nmID': nmID, 'vc': vc, 'title': title, 'len': len(title)})
    elif len(title) > 100:
        issues['long_title'].append({'nmID': nmID, 'vc': vc, 'title': title[:60], 'len': len(title)})
    
    # Characteristics check
    if len(chars) < 5:
        issues['few_chars'].append({'nmID': nmID, 'vc': vc, 'title': title[:50], 'count': len(chars)})
    
    # Brand check
    if not brand:
        issues['missing_brand'].append({'nmID': nmID, 'vc': vc, 'title': title[:50]})
    
    # Duplicate title tracking
    title_key = title.strip().lower()
    if title_key not in issues['duplicate_titles']:
        issues['duplicate_titles'][title_key] = []
    issues['duplicate_titles'][title_key].append(nmID)

# Find actual duplicates
duplicates = {k: v for k, v in issues['duplicate_titles'].items() if len(v) > 1}

# Print report
print("=" * 60)
print("1. ОПИСАНИЯ (DESCRIPTION)")
print("=" * 60)
avg_desc = total_desc_len / max(1, len(cards))
print(f"  Средняя длина: {avg_desc:.0f} символов")
print(f"  Без описания: {len(issues['no_desc'])}")
print(f"  Короткие (<500): {len(issues['short_desc'])}")
print(f"  Нормальные (500-2000): {len(cards) - len(issues['no_desc']) - len(issues['short_desc']) - len(issues['long_desc'])}")
print(f"  Длинные (>2000): {len(issues['long_desc'])}")
if issues['short_desc']:
    print("\n  Короткие описания:")
    for s in issues['short_desc'][:10]:
        print(f"    [{s['vc']}] {s['title']} — {s['len']} симв.")

print(f"\n{'=' * 60}")
print("2. ФОТОГРАФИИ")
print("=" * 60)
avg_photos = total_photo_count / max(1, len(cards))
print(f"  Среднее кол-во фото: {avg_photos:.1f}")
print(f"  Без фото: {len(issues['no_photos'])}")
print(f"  Мало фото (<3): {len(issues['few_photos'])}")
if issues['few_photos']:
    print("\n  Карточки с <3 фото:")
    for p in issues['few_photos'][:10]:
        print(f"    [{p['vc']}] {p['title']} — {p['count']} фото")

print(f"\n{'=' * 60}")
print("3. НАЗВАНИЯ (TITLE)")
print("=" * 60)
print(f"  Короткие (<30 симв): {len(issues['short_title'])}")
print(f"  Длинные (>100 симв): {len(issues['long_title'])}")
print(f"  Дубли названий: {len(duplicates)} групп ({sum(len(v) for v in duplicates.values())} карточек)")
if issues['short_title']:
    print("\n  Короткие названия:")
    for t in issues['short_title'][:10]:
        print(f"    [{t['vc']}] \"{t['title']}\" — {t['len']} симв.")

print(f"\n{'=' * 60}")
print("4. ХАРАКТЕРИСТИКИ")
print("=" * 60)
avg_chars = total_char_count / max(1, len(cards))
print(f"  Среднее кол-во характеристик: {avg_chars:.1f}")
print(f"  Мало характеристик (<5): {len(issues['few_chars'])}")
print(f"\n  Заполняемость характеристик (ТОП-20):")
sorted_chars = sorted(char_names_all.items(), key=lambda x: -x[1])
for name, count in sorted_chars[:20]:
    pct = count / len(cards) * 100
    print(f"    {name}: {count}/{len(cards)} ({pct:.0f}%)")

print(f"\n{'=' * 60}")
print("5. БРЕНД")
print("=" * 60)
print(f"  Без бренда: {len(issues['missing_brand'])}")

# Save detailed report
report = {
    'total_cards': len(cards),
    'avg_desc_len': round(avg_desc),
    'avg_photos': round(avg_photos, 1),
    'avg_chars': round(avg_chars, 1),
    'issues': {
        'no_desc': len(issues['no_desc']),
        'short_desc': len(issues['short_desc']),
        'few_photos': len(issues['few_photos']),
        'short_title': len(issues['short_title']),
        'duplicate_titles': len(duplicates),
        'few_chars': len(issues['few_chars']),
        'missing_brand': len(issues['missing_brand'])
    },
    'short_desc_list': issues['short_desc'],
    'few_photos_list': issues['few_photos'],
    'short_title_list': issues['short_title'],
    'duplicate_title_groups': {k: v for k, v in duplicates.items()},
}

with open('wb_full_audit_report.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"\nFull report saved to wb_full_audit_report.json")

# Summary
print(f"\n{'=' * 60}")
print("ИТОГО: ТОЧКИ РОСТА")
print("=" * 60)
total_issues = (len(issues['short_desc']) + len(issues['few_photos']) + 
                len(issues['short_title']) + len(duplicates))
print(f"  Критичных проблем: {total_issues}")
print(f"  1. Расширить {len(issues['short_desc'])} коротких описаний до 1000+ символов")
if issues['few_photos']:
    print(f"  2. Добавить фото к {len(issues['few_photos'])} карточкам (нужно минимум 3)")
if issues['short_title']:
    print(f"  3. Удлинить {len(issues['short_title'])} коротких названий (SEO-ключевые слова)")
if duplicates:
    print(f"  4. Уникализировать {len(duplicates)} групп с одинаковыми названиями")
