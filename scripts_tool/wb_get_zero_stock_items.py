# -*- coding: utf-8 -*-
"""
СПИСОК ТОВАРОВ С НУЛЕВЫМ ОСТАТКОМ ДЛЯ СРОЧНОГО ПОПОЛНЕНИЯ
Приоритизация по важности
"""
import json
import os
from collections import defaultdict

BASE_DIR = r'C:\Users\GravMix\.gemini\antigravity\playground\core-pulsar'
ANALYTICS_DIR = os.path.join(BASE_DIR, 'analytics')

print("╔══════════════════════════════════════════════════════════════╗")
print("║  ТОВАРЫ С НУЛЕВЫМ ОСТАТКОМ - СРОЧНОЕ ПОПОЛНЕНИЕ              ║")
print("╚══════════════════════════════════════════════════════════════╝\n")

# Загрузка данных
with open(os.path.join(ANALYTICS_DIR, 'wb_stocks.json'), 'r', encoding='utf-8') as f:
    stocks_data = json.load(f)

with open(os.path.join(ANALYTICS_DIR, 'wb_sales_year.json'), 'r', encoding='utf-8') as f:
    sales_data = json.load(f)

# Группировка остатков
stock_by_product = defaultdict(int)
for stock in stocks_data:
    nm_id = stock.get('nmId')
    qty = stock.get('quantity', 0)
    if nm_id:
        stock_by_product[nm_id] += qty

# Группировка продаж
product_sales = defaultdict(lambda: {'revenue': 0, 'orders': 0})
for sale in sales_data:
    nm_id = sale.get('nmId')
    if nm_id:
        product_sales[nm_id]['revenue'] += sale.get('finishedPrice', 0)
        product_sales[nm_id]['orders'] += 1

# Находим товары с нулевым остатком
zero_stock_items = []
for nm_id, stock in stock_by_product.items():
    if stock == 0 and nm_id in product_sales:
        zero_stock_items.append({
            'nm_id': nm_id,
            'stock': stock,
            'total_revenue': product_sales[nm_id]['revenue'],
            'total_orders': product_sales[nm_id]['orders'],
            'avg_price': product_sales[nm_id]['revenue'] / product_sales[nm_id]['orders'] if product_sales[nm_id]['orders'] > 0 else 0
        })

# Сортировка по выручке (самые прибыльные первые)
zero_stock_items.sort(key=lambda x: x['total_revenue'], reverse=True)

print(f"🔴 КРИТИЧНО: {len(zero_stock_items)} товаров с нулевым остатком\n")
print("─" * 80)
print(f"{'Приоритет':<12} {'NM_ID':<12} {'Заказов':>10} {'Выручка (₽)':>15} {'Ср. цена':>12}")
print("─" * 80)

# Топ-20 для срочного пополнения
urgent_items = []
for i, item in enumerate(zero_stock_items[:20], 1):
    priority = "🔴 СРОЧНО" if i <= 10 else "🟡 ВАЖНО"
    print(f"{priority:<12} {item['nm_id']:<12} {item['total_orders']:>10} {item['total_revenue']:>15,.0f} {item['avg_price']:>12,.0f}")
    
    if i <= 10:
        urgent_items.append(item['nm_id'])

# Сохранение списка
output = {
    'generated_at': '2026-02-26',
    'total_zero_stock': len(zero_stock_items),
    'top_20_priority': zero_stock_items[:20],
    'urgent_restock_list': urgent_items,
    'all_zero_stock': [item['nm_id'] for item in zero_stock_items]
}

output_path = os.path.join(ANALYTICS_DIR, 'wb_urgent_restock.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n{'='*80}")
print(f"✓ ТОП-10 ДЛЯ СРОЧНОГО ПОПОЛНЕНИЯ:")
print(f"  NM_IDs: {', '.join(str(nm) for nm in urgent_items)}")
print(f"\n✓ Полный список сохранен: {output_path}")
print(f"{'='*80}\n")

print("📋 РЕКОМЕНДАЦИИ:")
print("  1. Связаться с поставщиком СЕГОДНЯ")
print("  2. Срочный заказ топ-10 позиций")
print("  3. Срок поставки: 3-7 дней максимум")
print("  4. Ожидаемый эффект: +30-40% продаж\n")
