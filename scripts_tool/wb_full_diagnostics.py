# -*- coding: utf-8 -*-
"""
КОМПЛЕКСНАЯ ПРОВЕРКА И АНАЛИТИКА WILDBERRIES
Получение статистики продаж за год и диагностика проблем
"""
import json
import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any

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
print("║  КОМПЛЕКСНАЯ ПРОВЕРКА WILDBERRIES - GRAVMIX                  ║")
print("╚══════════════════════════════════════════════════════════════╝\n")

# ===== 1. ПОЛУЧЕНИЕ СПИСКА ВСЕХ КАРТОЧЕК =====
print("📋 1. ПОЛУЧЕНИЕ АКТУАЛЬНЫХ ДАННЫХ КАРТОЧЕК...")
print("─" * 60)

CARDS_URL = 'https://content-api.wildberries.ru/content/v2/get/cards/list'
cards_payload = {
    "settings": {
        "cursor": {"limit": 1000},
        "filter": {"withPhoto": -1}
    }
}

try:
    r = requests.post(CARDS_URL, headers=headers, json=cards_payload, timeout=30)
    if r.status_code == 200:
        cards_data = r.json()
        cards = cards_data.get('cards', [])
        print(f"✓ Получено карточек: {len(cards)}")
        
        # Сохраняем актуальные данные
        with open(os.path.join(ANALYTICS_DIR, 'wb_current_cards.json'), 'w', encoding='utf-8') as f:
            json.dump(cards, f, ensure_ascii=False, indent=2)
    else:
        print(f"❌ Ошибка получения карточек: {r.status_code}")
        cards = []
except Exception as e:
    print(f"❌ Exception: {e}")
    cards = []

# ===== 2. ПРОВЕРКА НЕЗАПОЛНЕННЫХ КАРТОЧЕК =====
print(f"\n📊 2. АНАЛИЗ НЕЗАПОЛНЕННЫХ КАРТОЧЕК...")
print("─" * 60)

incomplete_cards = []
for card in cards:
    issues = []
    
    # Проверка фото
    if not card.get('photos') or len(card.get('photos', [])) < 4:
        issues.append('мало_фото')
    
    # Проверка описания
    desc = card.get('description', '')
    if len(desc) < 500:
        issues.append('короткое_описание')
    
    # Проверка характеристик
    chars = card.get('characteristics', [])
    if len(chars) < 5:
        issues.append('мало_характеристик')
    
    # Проверка бренда
    if not card.get('brand'):
        issues.append('нет_бренда')
    
    if issues:
        incomplete_cards.append({
            'nm_id': card.get('nmID'),
            'title': card.get('title'),
            'vendor_code': card.get('vendorCode'),
            'issues': issues
        })

print(f"⚠️ Незаполненных карточек: {len(incomplete_cards)}")
if incomplete_cards:
    print(f"\nПримеры проблем:")
    for i, card in enumerate(incomplete_cards[:5], 1):
        print(f"  {i}. NM_{card['nm_id']}: {', '.join(card['issues'])}")

# ===== 3. ПОЛУЧЕНИЕ СТАТИСТИКИ ПРОДАЖ ЗА ГОД =====
print(f"\n📈 3. ПОЛУЧЕНИЕ СТАТИСТИКИ ПРОДАЖ...")
print("─" * 60)

# Период: год назад до сегодня
date_to = datetime.now()
date_from = date_to - timedelta(days=365)

SALES_URL = 'https://statistics-api.wildberries.ru/api/v1/supplier/sales'
params = {
    'dateFrom': date_from.strftime('%Y-%m-%d'),
    'flag': 0  # 0 = продажи, 1 = возвраты
}

sales_data = []
try:
    r = requests.get(SALES_URL, headers=headers, params=params, timeout=30)
    if r.status_code == 200:
        sales_data = r.json()
        print(f"✓ Получено записей о продажах: {len(sales_data)}")
        
        # Сохраняем
        with open(os.path.join(ANALYTICS_DIR, 'wb_sales_year.json'), 'w', encoding='utf-8') as f:
            json.dump(sales_data, f, ensure_ascii=False, indent=2)
    else:
        print(f"❌ Ошибка получения продаж: {r.status_code}")
except Exception as e:
    print(f"❌ Exception: {e}")

# ===== 4. АНАЛИЗ ПРОДАЖ ПО МЕСЯЦАМ =====
print(f"\n📊 4. АНАЛИЗ ПРОДАЖ ПО МЕСЯЦАМ...")
print("─" * 60)

from collections import defaultdict

monthly_sales = defaultdict(lambda: {'quantity': 0, 'revenue': 0, 'orders': 0})

for sale in sales_data:
    sale_date = sale.get('date', '')
    if sale_date:
        try:
            dt = datetime.fromisoformat(sale_date.replace('Z', '+00:00'))
            month_key = dt.strftime('%Y-%m')
            
            monthly_sales[month_key]['quantity'] += sale.get('quantity', 0)
            monthly_sales[month_key]['revenue'] += sale.get('finishedPrice', 0)
            monthly_sales[month_key]['orders'] += 1
        except:
            pass

# Сортируем по месяцам
sorted_months = sorted(monthly_sales.items())

print(f"\n{'Месяц':<10} {'Продажи':>10} {'Заказов':>10} {'Выручка':>15}")
print("─" * 50)
for month, data in sorted_months:
    print(f"{month:<10} {data['quantity']:>10} {data['orders']:>10} {data['revenue']:>15,.0f} ₽")

# ===== 5. СРАВНЕНИЕ С ПРОШЛЫМ ГОДОМ =====
print(f"\n📉 5. СРАВНЕНИЕ С ПРОШЛЫМ ГОДОМ (февраль)...")
print("─" * 60)

# Текущий февраль 2026
current_feb = monthly_sales.get('2026-02', {'quantity': 0, 'revenue': 0})
# Февраль 2025
prev_feb = monthly_sales.get('2025-02', {'quantity': 0, 'revenue': 0})

if prev_feb['quantity'] > 0:
    change_qty = ((current_feb['quantity'] - prev_feb['quantity']) / prev_feb['quantity']) * 100
    change_rev = ((current_feb['revenue'] - prev_feb['revenue']) / prev_feb['revenue']) * 100
    
    print(f"Февраль 2025: {prev_feb['quantity']} шт, {prev_feb['revenue']:,.0f} ₽")
    print(f"Февраль 2026: {current_feb['quantity']} шт, {current_feb['revenue']:,.0f} ₽")
    print(f"\nИзменение:")
    print(f"  Продажи: {change_qty:+.1f}%")
    print(f"  Выручка: {change_rev:+.1f}%")
else:
    print("⚠️ Нет данных за февраль 2025 для сравнения")

# ===== 6. АНАЛИЗ ОСТАТКОВ =====
print(f"\n📦 6. ПОЛУЧЕНИЕ ДАННЫХ ПО ОСТАТКАМ...")
print("─" * 60)

STOCKS_URL = 'https://statistics-api.wildberries.ru/api/v1/supplier/stocks'
params = {'dateFrom': date_from.strftime('%Y-%m-%d')}

stocks_data = []
try:
    r = requests.get(STOCKS_URL, headers=headers, params=params, timeout=30)
    if r.status_code == 200:
        stocks_data = r.json()
        print(f"✓ Получено данных по остаткам: {len(stocks_data)}")
        
        # Сохраняем
        with open(os.path.join(ANALYTICS_DIR, 'wb_stocks.json'), 'w', encoding='utf-8') as f:
            json.dump(stocks_data, f, ensure_ascii=False, indent=2)
            
        # Подсчет нулевых остатков
        zero_stocks = [s for s in stocks_data if s.get('quantity', 0) == 0]
        print(f"⚠️ Товаров с нулевым остатком: {len(zero_stocks)}")
    else:
        print(f"❌ Ошибка получения остатков: {r.status_code}")
except Exception as e:
    print(f"❌ Exception: {e}")

# ===== 7. ПОЛУЧЕНИЕ ЗАКАЗОВ =====
print(f"\n📋 7. ПОЛУЧЕНИЕ ДАННЫХ ПО ЗАКАЗАМ...")
print("─" * 60)

ORDERS_URL = 'https://statistics-api.wildberries.ru/api/v1/supplier/orders'
params = {'dateFrom': date_from.strftime('%Y-%m-%d')}

orders_data = []
try:
    r = requests.get(ORDERS_URL, headers=headers, params=params, timeout=30)
    if r.status_code == 200:
        orders_data = r.json()
        print(f"✓ Получено заказов: {len(orders_data)}")
        
        # Сохраняем
        with open(os.path.join(ANALYTICS_DIR, 'wb_orders_year.json'), 'w', encoding='utf-8') as f:
            json.dump(orders_data, f, ensure_ascii=False, indent=2)
            
        # Анализ отмен
        cancelled = [o for o in orders_data if o.get('isCancel', False)]
        if orders_data:
            cancel_rate = (len(cancelled) / len(orders_data)) * 100
            print(f"⚠️ Процент отмен: {cancel_rate:.1f}% ({len(cancelled)} из {len(orders_data)})")
    else:
        print(f"❌ Ошибка получения заказов: {r.status_code}")
except Exception as e:
    print(f"❌ Exception: {e}")

# ===== 8. СОХРАНЕНИЕ ИТОГОВОГО ОТЧЕТА =====
report = {
    'generated_at': datetime.now().isoformat(),
    'summary': {
        'total_cards': len(cards),
        'incomplete_cards': len(incomplete_cards),
        'total_sales_records': len(sales_data),
        'total_orders': len(orders_data),
        'zero_stock_items': len(zero_stocks) if stocks_data else 0
    },
    'monthly_sales': dict(sorted_months),
    'february_comparison': {
        '2025': prev_feb,
        '2026': current_feb,
        'change_percent': {
            'quantity': change_qty if 'change_qty' in locals() else None,
            'revenue': change_rev if 'change_rev' in locals() else None
        }
    },
    'incomplete_cards': incomplete_cards[:50],  # Топ-50
    'issues_detected': []
}

# Определение проблем
if len(incomplete_cards) > 50:
    report['issues_detected'].append('КРИТИЧНО: Более 50 незаполненных карточек')

if 'change_qty' in locals() and change_qty < -20:
    report['issues_detected'].append(f'КРИТИЧНО: Падение продаж на {abs(change_qty):.0f}%')

if stocks_data and len(zero_stocks) > len(stocks_data) * 0.3:
    report['issues_detected'].append('КРИТИЧНО: >30% товаров с нулевым остатком')

with open(os.path.join(ANALYTICS_DIR, 'wb_diagnostic_report.json'), 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"\n{'='*60}")
print("ДИАГНОСТИКА ЗАВЕРШЕНА")
print(f"{'='*60}")
print(f"\n✓ Все отчеты сохранены в: {ANALYTICS_DIR}")
print(f"\n⚠️ ОБНАРУЖЕНО ПРОБЛЕМ: {len(report['issues_detected'])}")
for issue in report['issues_detected']:
    print(f"  • {issue}")
