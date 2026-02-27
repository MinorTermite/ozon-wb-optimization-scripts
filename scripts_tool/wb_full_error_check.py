# -*- coding: utf-8 -*-
"""
ПОЛНАЯ ПРОВЕРКА ОШИБОК WILDBERRIES КАБИНЕТА
Включая черновики, валидацию, низкие рейтинги
"""
import json
import os
import requests
import time
from collections import defaultdict

BASE_DIR = r'C:\Users\GravMix\.gemini\antigravity\playground\core-pulsar'
ENV_PATH = os.path.join(BASE_DIR, '.env')
ANALYTICS_DIR = os.path.join(BASE_DIR, 'analytics')
os.makedirs(ANALYTICS_DIR, exist_ok=True)

# Загрузка API ключа
WB_KEY = ''
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('WB_API_KEY='):
                WB_KEY = line.strip().split('=', 1)[1]
                break

if not WB_KEY:
    print("❌ Error: WB_API_KEY not found")
    exit(1)

headers = {
    'Authorization': WB_KEY,
    'Content-Type': 'application/json'
}

print("╔══════════════════════════════════════════════════════════════╗")
print("║  ПОЛНАЯ ПРОВЕРКА ОШИБОК WILDBERRIES КАБИНЕТА                 ║")
print("╚══════════════════════════════════════════════════════════════╝\n")

# ===== 1. ПОЛУЧЕНИЕ СПИСКА ОШИБОК =====
print("🔍 1. ПОЛУЧЕНИЕ СПИСКА ОШИБОК КАРТОЧЕК")
print("─" * 70)

ERRORS_URL = 'https://content-api.wildberries.ru/content/v2/cards/error/list'

try:
    r = requests.post(ERRORS_URL, headers=headers, json={}, timeout=30)
    if r.status_code == 200:
        errors_data = r.json()
        error_cards = errors_data.get('data', {}).get('cards', [])
        print(f"✓ Получено карточек с ошибками: {len(error_cards)}")
        
        # Группировка по типам ошибок
        errors_by_type = defaultdict(list)
        for card in error_cards:
            errors = card.get('errors', [])
            nm_id = card.get('nmID')
            vendor_code = card.get('vendorCode')
            
            for err in errors:
                err_key = err.get('key', 'unknown')
                errors_by_type[err_key].append({
                    'nm_id': nm_id,
                    'vendor_code': vendor_code,
                    'error': err
                })
        
        print(f"\nТипы ошибок:")
        for err_type, items in errors_by_type.items():
            print(f"  • {err_type}: {len(items)} карточек")
        
        # Сохраняем
        with open(os.path.join(ANALYTICS_DIR, 'wb_errors_full.json'), 'w', encoding='utf-8') as f:
            json.dump({
                'total_errors': len(error_cards),
                'errors_by_type': {k: len(v) for k, v in errors_by_type.items()},
                'details': error_cards
            }, f, ensure_ascii=False, indent=2)
    else:
        print(f"❌ Ошибка получения списка ошибок: {r.status_code}")
        error_cards = []
        errors_by_type = {}
except Exception as e:
    print(f"❌ Exception: {e}")
    error_cards = []
    errors_by_type = {}

# ===== 2. ПОЛУЧЕНИЕ ВСЕХ КАРТОЧЕК (включая черновики) =====
print(f"\n📋 2. ПОЛУЧЕНИЕ ВСЕХ КАРТОЧЕК")
print("─" * 70)

CARDS_URL = 'https://content-api.wildberries.ru/content/v2/get/cards/list'
cards_payload = {
    "settings": {
        "cursor": {"limit": 1000},
        "filter": {"withPhoto": -1}
    }
}

all_cards = []
try:
    r = requests.post(CARDS_URL, headers=headers, json=cards_payload, timeout=30)
    if r.status_code == 200:
        cards_data = r.json()
        all_cards = cards_data.get('cards', [])
        print(f"✓ Получено всего карточек: {len(all_cards)}")
    else:
        print(f"❌ Ошибка получения карточек: {r.status_code}")
except Exception as e:
    print(f"❌ Exception: {e}")

# ===== 3. АНАЛИЗ ЧЕРНОВИКОВ =====
print(f"\n📝 3. АНАЛИЗ ЧЕРНОВИКОВ И СТАТУСОВ")
print("─" * 70)

drafts = []
published = []
moderation = []

for card in all_cards:
    # Проверяем статус по наличию NM_ID
    nm_id = card.get('nmID')
    imt_id = card.get('imtID')
    
    if not nm_id or nm_id == 0:
        drafts.append(card)
    else:
        published.append(card)

print(f"Черновики: {len(drafts)}")
print(f"Опубликованные: {len(published)}")

# Детали черновиков
if drafts:
    print(f"\nПримеры черновиков:")
    for i, draft in enumerate(drafts[:10], 1):
        vc = draft.get('vendorCode', 'N/A')
        title = draft.get('title', 'N/A')[:50]
        print(f"  {i}. VC: {vc} | {title}")

# ===== 4. ПРОВЕРКА РЕЙТИНГОВ =====
print(f"\n⭐ 4. ПОИСК ТОВАРОВ С НИЗКИМ РЕЙТИНГОМ (<4.0)")
print("─" * 70)

low_rating_cards = []

# Для каждой опубликованной карточки проверяем рейтинг
# Рейтинг обычно в отдельном API, но можем проверить из данных карточки
for card in published:
    nm_id = card.get('nmID')
    # В API v2 нет рейтинга напрямую, нужно использовать Statistics API
    # Пока отмечаем для отдельной проверки

print(f"⚠️ Для точной проверки рейтингов нужен отдельный запрос к Statistics API")
print(f"Опубликованных карточек для проверки: {len(published)}")

# ===== 5. ПРОВЕРКА ОСТАТКОВ =====
print(f"\n📦 5. ПРОВЕРКА ОСТАТКОВ")
print("─" * 70)

# Уже есть данные из предыдущей диагностики
stocks_path = os.path.join(ANALYTICS_DIR, 'wb_stocks.json')
if os.path.exists(stocks_path):
    with open(stocks_path, 'r', encoding='utf-8') as f:
        stocks_data = json.load(f)
    
    stock_by_product = defaultdict(int)
    for stock in stocks_data:
        nm_id = stock.get('nmId')
        qty = stock.get('quantity', 0)
        if nm_id:
            stock_by_product[nm_id] += qty
    
    zero_stock = {nm for nm, qty in stock_by_product.items() if qty == 0}
    print(f"✓ Товаров с нулевым остатком: {len(zero_stock)}")
else:
    print(f"⚠️ Данные по остаткам не найдены")
    zero_stock = set()

# ===== 6. ВАЛИДАЦИЯ КАРТОЧЕК =====
print(f"\n🔧 6. ПРОВЕРКА ВАЛИДАЦИИ КАРТОЧЕК")
print("─" * 70)

validation_issues = {
    'no_brand': [],
    'short_title': [],
    'long_title': [],
    'no_description': [],
    'short_description': [],
    'no_dimensions': [],
    'no_weight': [],
    'no_photos': [],
    'few_photos': [],
    'no_characteristics': []
}

for card in all_cards:
    nm_id = card.get('nmID')
    vc = card.get('vendorCode')
    
    # Бренд
    if not card.get('brand'):
        validation_issues['no_brand'].append((nm_id, vc))
    
    # Заголовок
    title = card.get('title', '')
    if len(title) < 20:
        validation_issues['short_title'].append((nm_id, vc, len(title)))
    if len(title) > 60:
        validation_issues['long_title'].append((nm_id, vc, len(title)))
    
    # Описание
    desc = card.get('description', '')
    if not desc:
        validation_issues['no_description'].append((nm_id, vc))
    elif len(desc) < 100:
        validation_issues['short_description'].append((nm_id, vc, len(desc)))
    
    # Габариты
    dimensions = card.get('dimensions', {})
    if not dimensions or dimensions.get('width', 0) == 0:
        validation_issues['no_dimensions'].append((nm_id, vc))
    
    # Вес через характеристики
    chars = card.get('characteristics', [])
    has_weight = any(c.get('id') == 14177450 for c in chars)
    if not has_weight:
        validation_issues['no_weight'].append((nm_id, vc))
    
    # Фото
    photos = card.get('photos', [])
    if not photos:
        validation_issues['no_photos'].append((nm_id, vc))
    elif len(photos) < 4:
        validation_issues['few_photos'].append((nm_id, vc, len(photos)))
    
    # Характеристики
    if len(chars) < 3:
        validation_issues['no_characteristics'].append((nm_id, vc, len(chars)))

print("Найденные проблемы валидации:")
for issue_type, items in validation_issues.items():
    if items:
        print(f"  • {issue_type}: {len(items)} карточек")

# ===== 7. ИТОГОВЫЙ ОТЧЕТ =====
print(f"\n{'='*70}")
print("ИТОГОВЫЙ ОТЧЕТ ПО ОШИБКАМ")
print(f"{'='*70}")

report = {
    'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
    'summary': {
        'total_cards': len(all_cards),
        'drafts': len(drafts),
        'published': len(published),
        'cards_with_api_errors': len(error_cards),
        'zero_stock_items': len(zero_stock)
    },
    'api_errors': {
        'total': len(error_cards),
        'by_type': {k: len(v) for k, v in errors_by_type.items()},
        'details': list(errors_by_type.keys())
    },
    'validation_issues': {k: len(v) for k, v in validation_issues.items() if v},
    'drafts_list': [
        {'vendor_code': d.get('vendorCode'), 'title': d.get('title')[:50]}
        for d in drafts[:50]
    ],
    'critical_actions': []
}

# Определение критических действий
if len(error_cards) > 0:
    report['critical_actions'].append(f"🔴 Исправить {len(error_cards)} карточек с ошибками API")

if len(drafts) > 50:
    report['critical_actions'].append(f"🔴 Вывести из черновиков {len(drafts)} карточек")

if validation_issues['no_dimensions']:
    report['critical_actions'].append(f"🔴 Добавить габариты для {len(validation_issues['no_dimensions'])} карточек")

if validation_issues['long_title']:
    report['critical_actions'].append(f"🟡 Сократить заголовки для {len(validation_issues['long_title'])} карточек")

if len(zero_stock) > 30:
    report['critical_actions'].append(f"🔴 Пополнить остатки для {len(zero_stock)} товаров")

print(f"\n🔴 КРИТИЧЕСКИЕ ПРОБЛЕМЫ:")
for action in report['critical_actions']:
    print(f"  {action}")

# Сохранение отчета
with open(os.path.join(ANALYTICS_DIR, 'wb_full_error_report.json'), 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"\n✓ Полный отчет сохранен:")
print(f"  {os.path.join(ANALYTICS_DIR, 'wb_full_error_report.json')}")
print(f"\n{'='*70}\n")
