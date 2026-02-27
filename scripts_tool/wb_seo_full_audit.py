# -*- coding: utf-8 -*-
import os, json, re
from collections import defaultdict, Counter
from typing import List, Dict

BASE_DIR = r'C:\Users\GravMix\.gemini\antigravity\playground\core-pulsar'
DUMP = os.path.join(BASE_DIR, 'data_dump', 'wb_cards_seo_dump.json')
REPORT = os.path.join(BASE_DIR, 'WB_SEO_AUDIT.md')

print("🔍 Загрузка карточек...")
with open(DUMP, encoding='utf-8') as f:
    cards = json.load(f)
print(f"✓ Загружено: {len(cards)} карточек\n")

# Статистика
stats = {
    'total': len(cards),
    'short_title': 0,  # < 30 символов
    'long_title': 0,   # > 60 символов
    'no_keywords': 0,  # нет ключевых слов 2026
    'short_desc': 0,   # < 500 символов
    'few_photos': 0,   # < 5 фото
    'no_video': 0,
    'no_brand': 0,
    'low_chars': 0     # < 5 характеристик
}

issues_by_card = []
KEYWORDS = ['гравировка', '2026', 'именной', 'персональный']

print("📊 Анализирую карточки...\n")
for idx, card in enumerate(cards, 1):
    nmid = card.get('nmID')
    title = str(card.get('title', ''))
    desc = str(card.get('description', ''))
    photos = len(card.get('photos', []))
    video = bool(card.get('video'))
    brand = str(card.get('brand', '')).strip()
    chars = len(card.get('characteristics', []))
    
    card_issues = []
    score = 100
    
    # Проверка заголовка
    if len(title) < 30:
        stats['short_title'] += 1
        card_issues.append(f"❌ Короткий заголовок ({len(title)} симв.)")
        score -= 20
    elif len(title) > 60:
        stats['long_title'] += 1
        card_issues.append(f"⚠️ Превышен лимит ({len(title)} симв. > 60)")
        score -= 15
    
    if not any(kw in title.lower() for kw in KEYWORDS):
        stats['no_keywords'] += 1
        card_issues.append("❌ Нет ключевых слов 2026")
        score -= 25
    
    # Проверка описания
    if len(desc) < 500:
        stats['short_desc'] += 1
        card_issues.append(f"❌ Короткое описание ({len(desc)} симв.)")
        score -= 20
    
    # Проверка фото
    if photos < 5:
        stats['few_photos'] += 1
        card_issues.append(f"⚠️ Мало фото ({photos} шт.)")
        score -= 15
    
    if not video:
        stats['no_video'] += 1
        card_issues.append("❌ Нет видео")
        score -= 20
    
    # Проверка бренда
    if not brand:
        stats['no_brand'] += 1
        card_issues.append("❌ Не указан бренд")
        score -= 20
    
    # Проверка характеристик
    if chars < 5:
        stats['low_chars'] += 1
        card_issues.append(f"⚠️ Мало характеристик ({chars} шт.)")
        score -= 15
    
    if card_issues:
        issues_by_card.append({
            'nmID': nmid,
            'score': max(0, score),
            'issues': card_issues,
            'title': title[:60] + '...' if len(title) > 60 else title
        })
    
    if idx % 50 == 0:
        print(f"   Обработано {idx}/{len(cards)}...")

# Сортировка по score
issues_by_card.sort(key=lambda x: x['score'])

# Формирование отчета
report = f"""# 📊 WB SEO АУДИТ - ЭКСПРЕСС АНАЛИЗ
**Дата:** 26.02.2026  
**Карточек проанализировано:** {stats['total']}

## 🎯 КРИТИЧЕСКИЕ ПРОБЛЕМЫ

| Проблема | Количество | % |
|----------|------------|---|
| Короткий заголовок (< 30 симв.) | {stats['short_title']} | {stats['short_title']/stats['total']*100:.1f}% |
| Превышен лимит заголовка (> 60) | {stats['long_title']} | {stats['long_title']/stats['total']*100:.1f}% |
| Нет ключевых слов 2026 | {stats['no_keywords']} | {stats['no_keywords']/stats['total']*100:.1f}% |
| Короткое описание (< 500) | {stats['short_desc']} | {stats['short_desc']/stats['total']*100:.1f}% |
| Мало фото (< 5) | {stats['few_photos']} | {stats['few_photos']/stats['total']*100:.1f}% |
| Нет видео | {stats['no_video']} | {stats['no_video']/stats['total']*100:.1f}% |
| Не указан бренд | {stats['no_brand']} | {stats['no_brand']/stats['total']*100:.1f}% |
| Мало характеристик (< 5) | {stats['low_chars']} | {stats['low_chars']/stats['total']*100:.1f}% |

## 🚨 ТОП-20 КАРТОЧЕК ТРЕБУЮЩИХ СРОЧНОЙ ОПТИМИЗАЦИИ

"""

for i, card in enumerate(issues_by_card[:20], 1):
    report += f"\n### {i}. NM: {card['nmID']} | Score: {card['score']}/100\n"
    report += f"**Заголовок:** {card['title']}\n\n"
    report += "**Проблемы:**\n"
    for issue in card['issues']:
        report += f"- {issue}\n"

report += f"""

## ✅ РЕКОМЕНДАЦИИ

### 1. ЗАГОЛОВКИ (Приоритет: ВЫСОКИЙ)
- Оптимальная длина: 50-60 символов
- Обязательно включить: "гравировка 2026"
- Формат: "[Категория] [ключевые слова] гравировка 2026"

### 2. ОПИСАНИЯ (Приоритет: ВЫСОКИЙ)
- Минимум: 1000 символов
- Структура: Введение + Преимущества + Характеристики + Призыв к действию
- Ключевые слова: 3-7 упоминаний на 1000 символов

### 3. МЕДИА (Приоритет: СРЕДНИЙ)
- Фото: минимум 8 шт., оптимально 12-15
- Видео: ОБЯЗАТЕЛЬНО (повышает конверсию на 30-50%)

### 4. БРЕНД (Приоритет: ВЫСОКИЙ)
- Указать "GRAVMIX" для ВСЕХ карточек

### 5. ХАРАКТЕРИСТИКИ (Приоритет: СРЕДНИЙ)
- Заполнить ВСЕ доступные поля
- Минимум 10 характеристик

## 📈 СЛЕДУЮЩИЕ ШАГИ

1. Запустить скрипт автоматической оптимизации:
   ```
   python scripts_tool\\wb_seo_apply_2026_FIXED.py
   ```

2. Добавить видео и фото вручную через личный кабинет WB

3. Повторить аудит через 48 часов после индексации

---
**Аудит выполнен:** Claude SEO Auditor
"""

# Сохранение отчета
with open(REPORT, 'w', encoding='utf-8') as f:
    f.write(report)

print(f"\n✅ АУДИТ ЗАВЕРШЕН!")
print(f"📊 Карточек с проблемами: {len(issues_by_card)} ({len(issues_by_card)/stats['total']*100:.1f}%)")
print(f"📁 Отчет сохранен: {REPORT}")
print(f"\n🔝 ТОП-3 проблемы:")
print(f"1. Нет ключевых слов 2026: {stats['no_keywords']} карточек")
print(f"2. Нет видео: {stats['no_video']} карточек")
print(f"3. Короткое описание: {stats['short_desc']} карточек")
