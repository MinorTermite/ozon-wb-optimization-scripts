# -*- coding: utf-8 -*-
"""
WB: Find EXACT cards with missing characteristics, prepare fix plan
"""
import json

with open('wb_cards_seo_dump.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

# Define required characteristics per subject
REQUIRED = {
    201: {  # Браслеты
        'Страна производства': 'Россия',
        'Повод': ['день рождения', 'просто так', 'новый год', '14 февраля', '23 февраля', '8 марта'],
        'Назначение подарка': ['для мужчины', 'для женщины'],
        'Вид браслета': 'плетёнка',
        'Тип подарка': ['подарок — украшение', 'памятный подарок'],
        'Назначение': ['аксессуар'],
        'Пол': 'Унисекс',
    },
    297: {  # Брелоки
        'Ставка НДС': 'Без НДС',
        'Тип подарка': ['подарок — аксессуар', 'памятный подарок'],
        'Декоративные элементы': ['гравировка'],
        'Вид замка': 'карабин',
        'Комплектация': 'Брелок',
        'Повод': ['день рождения', 'просто так'],
        'Назначение подарка': ['для мужчины', 'для женщины'],
        'Эффекты': ['без эффектов'],
        'Высота предмета': '5',
        'Ширина предмета': '3',
        'Количество предметов в упаковке': '1',
        'Назначение': ['для ключей'],
    },
    298: {  # Подвески
        'Покрытие': 'медицинский сплав',
        'Тип подарка': ['подарок — украшение'],
        'Вид подвески': 'подвеска',
        'Вставка': 'без вставки',
        'Пол': 'Унисекс',
        'Назначение подарка': ['для мужчины', 'для женщины'],
    }
}

# Find gaps per card
gaps = []
for c in cards:
    sid = c.get('subjectID')
    if sid not in REQUIRED:
        continue
    
    char_names = set()
    for ch in c.get('characteristics', []):
        char_names.add(ch.get('name', ''))
    
    missing = []
    for req_name in REQUIRED[sid]:
        if req_name not in char_names:
            missing.append(req_name)
    
    if missing:
        gaps.append({
            'nmID': c['nmID'],
            'vc': c['vendorCode'],
            'subjectID': sid,
            'subjectName': c.get('subjectName', ''),
            'title': c['title'][:50],
            'missing': missing,
            'missing_count': len(missing)
        })

print(f"Cards with missing characteristics: {len(gaps)}")
print()

# Group by subject
from collections import defaultdict
by_subject = defaultdict(list)
for g in gaps:
    by_subject[g['subjectName']].append(g)

for sname, items in by_subject.items():
    print(f"=== {sname} ({len(items)} cards) ===")
    
    # Count missing fields
    field_counts = defaultdict(int)
    for item in items:
        for m in item['missing']:
            field_counts[m] += 1
    
    print("  Missing fields:")
    for fn, cnt in sorted(field_counts.items(), key=lambda x: -x[1]):
        print(f"    {fn}: {cnt} cards")
    
    print(f"\n  Sample cards:")
    for item in items[:3]:
        print(f"    [{item['vc']}] {item['title']} — missing: {', '.join(item['missing'])}")
    print()

# Save for fix script
with open('wb_missing_chars.json', 'w', encoding='utf-8') as f:
    json.dump(gaps, f, ensure_ascii=False, indent=2)
print(f"\nSaved {len(gaps)} cards with gaps to wb_missing_chars.json")
