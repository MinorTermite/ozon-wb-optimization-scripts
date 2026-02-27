# -*- coding: utf-8 -*-
"""
WILDBERRIES SEO АУДИТ И ОПТИМИЗАЦИЯ
Комплексный анализ 266 карточек GRAVMIX
"""
import json
import os
from typing import List, Dict, Any
from collections import defaultdict, Counter

BASE_DIR = r'C:\Users\GravMix\.gemini\antigravity\playground\core-pulsar'
DUMP_PATH = os.path.join(BASE_DIR, 'data_dump', 'wb_cards_seo_dump.json')
AUDIT_REPORT = os.path.join(BASE_DIR, 'WB_SEO_AUDIT_REPORT.json')
OPTIMIZATION_PLAN = os.path.join(BASE_DIR, 'WB_SEO_OPTIMIZATION_PLAN.json')

# Загрузка карточек
with open(DUMP_PATH, 'r', encoding='utf-8') as f:
    cards = json.load(f)

print(f"╔══════════════════════════════════════════════════════════════╗")
print(f"║  WILDBERRIES SEO АУДИТ - GRAVMIX                             ║")
print(f"║  Карточек: {len(cards):3d}                                             ║")
print(f"╚══════════════════════════════════════════════════════════════╝\n")

# ===== 1. АНАЛИЗ ЗАГОЛОВКОВ =====
print("📋 1. АНАЛИЗ ЗАГОЛОВКОВ")
print("─" * 60)

title_issues = {
    'too_long': [],      # > 60 символов
    'too_short': [],     # < 20 символов
    'no_keywords': [],   # нет ключевых слов
    'generic': [],       # Generic названия
    'no_brand': [],      # нет упоминания бренда
    'good': []           # хорошие заголовки
}

keywords_2026 = ['гравировка', '2026', '2027', 'именной', 'браслет', 'подарок', 'сталь']

for card in cards:
    title = card.get('title', '')
    nm_id = card.get('nmID')
    
    if len(title) > 60:
        title_issues['too_long'].append({'nm_id': nm_id, 'title': title, 'len': len(title)})
    elif len(title) < 20:
        title_issues['too_short'].append({'nm_id': nm_id, 'title': title, 'len': len(title)})
    
    title_lower = title.lower()
    has_keywords = any(kw in title_lower for kw in keywords_2026)
    
    if not has_keywords:
        title_issues['no_keywords'].append({'nm_id': nm_id, 'title': title})
    
    # Проверка на generic названия
    generic_names = ['браслет', 'именной', 'зодиак', 'армия']
    if title.lower().strip() in generic_names:
        title_issues['generic'].append({'nm_id': nm_id, 'title': title})
    
    if 'gravmix' not in title_lower and 'грав' not in title_lower:
        title_issues['no_brand'].append({'nm_id': nm_id, 'title': title})
    
    # Хорошие заголовки
    if 20 <= len(title) <= 60 and has_keywords:
        title_issues['good'].append({'nm_id': nm_id, 'title': title})

print(f"✓ Хорошие заголовки: {len(title_issues['good'])}")
print(f"⚠ Слишком длинные (>60): {len(title_issues['too_long'])}")
print(f"⚠ Слишком короткие (<20): {len(title_issues['too_short'])}")
print(f"⚠ Без ключевых слов: {len(title_issues['no_keywords'])}")
print(f"⚠ Generic названия: {len(title_issues['generic'])}")
print(f"⚠ Без бренда: {len(title_issues['no_brand'])}\n")

# ===== 2. АНАЛИЗ ОПИСАНИЙ =====
print("📝 2. АНАЛИЗ ОПИСАНИЙ")
print("─" * 60)

desc_issues = {
    'too_short': [],     # < 500 символов
    'no_keywords': [],   # нет ключевых слов
    'no_usp': [],        # нет УТП
    'no_call': [],       # нет призыва к действию
    'good': []
}

usp_keywords = ['нержавеющая сталь', '316l', 'гравировка', 'персонализация', 'подарок']
call_to_action = ['заказ', 'купи', 'подар', 'закаж']

for card in cards:
    desc = card.get('description', '')
    nm_id = card.get('nmID')
    
    if len(desc) < 500:
        desc_issues['too_short'].append({'nm_id': nm_id, 'len': len(desc)})
    
    desc_lower = desc.lower()
    has_keywords = any(kw in desc_lower for kw in keywords_2026)
    has_usp = any(kw in desc_lower for kw in usp_keywords)
    has_call = any(kw in desc_lower for kw in call_to_action)
    
    if not has_keywords:
        desc_issues['no_keywords'].append({'nm_id': nm_id})
    if not has_usp:
        desc_issues['no_usp'].append({'nm_id': nm_id})
    if not has_call:
        desc_issues['no_call'].append({'nm_id': nm_id})
    
    if len(desc) >= 500 and has_keywords and has_usp:
        desc_issues['good'].append({'nm_id': nm_id})

print(f"✓ Качественные описания: {len(desc_issues['good'])}")
print(f"⚠ Слишком короткие (<500): {len(desc_issues['too_short'])}")
print(f"⚠ Без ключевых слов: {len(desc_issues['no_keywords'])}")
print(f"⚠ Без УТП: {len(desc_issues['no_usp'])}")
print(f"⚠ Без призыва к действию: {len(desc_issues['no_call'])}\n")

# ===== 3. АНАЛИЗ ФОТО =====
print("📸 3. АНАЛИЗ ФОТОГРАФИЙ")
print("─" * 60)

photo_stats = {
    'no_photos': [],
    'few_photos': [],    # < 4 фото
    'optimal': [],       # 4-8 фото
    'good': []           # 8+ фото
}

for card in cards:
    nm_id = card.get('nmID')
    photos = card.get('photos', [])
    count = len(photos)
    
    if count == 0:
        photo_stats['no_photos'].append({'nm_id': nm_id})
    elif count < 4:
        photo_stats['few_photos'].append({'nm_id': nm_id, 'count': count})
    elif count <= 8:
        photo_stats['optimal'].append({'nm_id': nm_id, 'count': count})
    else:
        photo_stats['good'].append({'nm_id': nm_id, 'count': count})

print(f"✓ Хорошее количество (8+): {len(photo_stats['good'])}")
print(f"✓ Оптимальное (4-8): {len(photo_stats['optimal'])}")
print(f"⚠ Мало фото (<4): {len(photo_stats['few_photos'])}")
print(f"⚠ Нет фото: {len(photo_stats['no_photos'])}\n")

# ===== 4. АНАЛИЗ ХАРАКТЕРИСТИК =====
print("🏷️ 4. АНАЛИЗ ХАРАКТЕРИСТИК")
print("─" * 60)

char_stats = {
    'few_chars': [],     # < 5 характеристик
    'good': []           # 5+ характеристик
}

for card in cards:
    nm_id = card.get('nmID')
    chars = card.get('characteristics', [])
    count = len(chars)
    
    if count < 5:
        char_stats['few_chars'].append({'nm_id': nm_id, 'count': count})
    else:
        char_stats['good'].append({'nm_id': nm_id, 'count': count})

print(f"✓ Достаточно характеристик (5+): {len(char_stats['good'])}")
print(f"⚠ Мало характеристик (<5): {len(char_stats['few_chars'])}\n")

# ===== 5. КАТЕГОРИЗАЦИЯ ПО ТИПУ =====
print("🎯 5. КАТЕГОРИЗАЦИЯ ПО ТИПУ ПРОДУКТА")
print("─" * 60)

categories = defaultdict(list)

for card in cards:
    nm_id = card.get('nmID')
    title = card.get('title', '').lower()
    vc = card.get('vendorCode', '').lower()
    
    if 'именной' in title or 'именной' in vc:
        categories['Именные'].append(nm_id)
    elif 'зодиак' in title or 'зодиак' in vc:
        categories['Зодиак'].append(nm_id)
    elif 'армия' in title or 'армия' in vc:
        categories['Армия'].append(nm_id)
    elif 'семья' in title or 'семья' in vc:
        categories['Семья'].append(nm_id)
    else:
        categories['Другое'].append(nm_id)

for cat, items in sorted(categories.items()):
    print(f"{cat}: {len(items)} карточек")

print()

# ===== 6. ОБЩИЙ РЕЙТИНГ SEO =====
print("⭐ 6. ОБЩИЙ РЕЙТИНГ SEO")
print("─" * 60)

seo_scores = []

for card in cards:
    nm_id = card.get('nmID')
    score = 0
    issues = []
    
    # Заголовок (30 баллов)
    title = card.get('title', '')
    if 20 <= len(title) <= 60:
        score += 10
    else:
        issues.append('title_length')
    
    if any(kw in title.lower() for kw in keywords_2026):
        score += 20
    else:
        issues.append('title_keywords')
    
    # Описание (30 баллов)
    desc = card.get('description', '')
    if len(desc) >= 500:
        score += 10
    else:
        issues.append('desc_length')
    
    if any(kw in desc.lower() for kw in keywords_2026):
        score += 10
    else:
        issues.append('desc_keywords')
    
    if any(kw in desc.lower() for kw in usp_keywords):
        score += 10
    else:
        issues.append('desc_usp')
    
    # Фото (20 баллов)
    photos = len(card.get('photos', []))
    if photos >= 8:
        score += 20
    elif photos >= 4:
        score += 10
    else:
        issues.append('photos')
    
    # Характеристики (20 баллов)
    chars = len(card.get('characteristics', []))
    if chars >= 5:
        score += 20
    elif chars >= 3:
        score += 10
    else:
        issues.append('characteristics')
    
    seo_scores.append({
        'nm_id': nm_id,
        'score': score,
        'issues': issues,
        'title': title
    })

# Сортировка по рейтингу
seo_scores.sort(key=lambda x: x['score'], reverse=True)

# Статистика по баллам
excellent = [s for s in seo_scores if s['score'] >= 80]
good = [s for s in seo_scores if 60 <= s['score'] < 80]
average = [s for s in seo_scores if 40 <= s['score'] < 60]
poor = [s for s in seo_scores if s['score'] < 40]

print(f"🏆 Отлично (80-100): {len(excellent)} карточек")
print(f"✓ Хорошо (60-79): {len(good)} карточек")
print(f"⚠ Средне (40-59): {len(average)} карточек")
print(f"❌ Плохо (<40): {len(poor)} карточек\n")

print(f"Средний балл: {sum(s['score'] for s in seo_scores) / len(seo_scores):.1f}/100\n")

# ===== 7. ТОП-10 ЛУЧШИХ И ХУДШИХ =====
print("🏆 ТОП-10 ЛУЧШИХ КАРТОЧЕК")
print("─" * 60)
for i, item in enumerate(seo_scores[:10], 1):
    print(f"{i}. NM_{item['nm_id']}: {item['score']} баллов")
    print(f"   {item['title'][:50]}...")

print(f"\n❌ ТОП-10 ХУДШИХ КАРТОЧЕК (требуют срочной оптимизации)")
print("─" * 60)
for i, item in enumerate(seo_scores[-10:], 1):
    print(f"{i}. NM_{item['nm_id']}: {item['score']} баллов")
    print(f"   Проблемы: {', '.join(item['issues'])}")

# ===== СОХРАНЕНИЕ ОТЧЕТА =====
audit_data = {
    'summary': {
        'total_cards': len(cards),
        'avg_score': sum(s['score'] for s in seo_scores) / len(seo_scores),
        'excellent': len(excellent),
        'good': len(good),
        'average': len(average),
        'poor': len(poor)
    },
    'title_issues': title_issues,
    'desc_issues': desc_issues,
    'photo_stats': photo_stats,
    'char_stats': char_stats,
    'categories': {k: len(v) for k, v in categories.items()},
    'seo_scores': seo_scores
}

with open(AUDIT_REPORT, 'w', encoding='utf-8') as f:
    json.dump(audit_data, f, ensure_ascii=False, indent=2)

print(f"\n✓ Полный отчет сохранен: {AUDIT_REPORT}")
print(f"\nГотовлю план оптимизации...")
