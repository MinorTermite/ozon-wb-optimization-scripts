# -*- coding: utf-8 -*-
"""
АНАЛИЗ ПРИЧИН УПАДКА ПРОДАЖ WILDBERRIES
Детальное исследование и план восстановления
"""
import json
import os
from datetime import datetime
from collections import defaultdict, Counter

BASE_DIR = r'C:\Users\GravMix\.gemini\antigravity\playground\core-pulsar'
ANALYTICS_DIR = os.path.join(BASE_DIR, 'analytics')

print("╔══════════════════════════════════════════════════════════════╗")
print("║  АНАЛИЗ ПРИЧИН УПАДКА ПРОДАЖ - GRAVMIX                       ║")
print("╚══════════════════════════════════════════════════════════════╝\n")

# Загрузка данных
with open(os.path.join(ANALYTICS_DIR, 'wb_diagnostic_report.json'), 'r', encoding='utf-8') as f:
    report = json.load(f)

with open(os.path.join(ANALYTICS_DIR, 'wb_sales_year.json'), 'r', encoding='utf-8') as f:
    sales_data = json.load(f)

with open(os.path.join(ANALYTICS_DIR, 'wb_stocks.json'), 'r', encoding='utf-8') as f:
    stocks_data = json.load(f)

# ===== АНАЛИЗ ДИНАМИКИ =====
print("📊 ДИНАМИКА ПРОДАЖ (последние 12 месяцев)")
print("─" * 70)

monthly = report['monthly_sales']
sorted_months = sorted(monthly.items(), reverse=True)[:12]

print(f"{'Месяц':<12} {'Заказов':>10} {'Выручка (₽)':>15} {'Средний чек':>12}")
print("─" * 70)

avg_checks = []
for month, data in sorted_months:
    avg_check = data['revenue'] / data['orders'] if data['orders'] > 0 else 0
    avg_checks.append(avg_check)
    print(f"{month:<12} {data['orders']:>10} {data['revenue']:>15,.0f} {avg_check:>12,.0f}")

# ===== ВЫЯВЛЕНИЕ ПАДЕНИЯ =====
print(f"\n🔍 АНАЛИЗ ПАДЕНИЯ")
print("─" * 70)

dec_2025 = monthly.get('2025-12', {})
jan_2026 = monthly.get('2026-01', {})
feb_2026 = monthly.get('2026-02', {})

dec_orders = dec_2025.get('orders', 0)
feb_orders = feb_2026.get('orders', 0)

if dec_orders > 0:
    drop_percent = ((feb_orders - dec_orders) / dec_orders) * 100
    print(f"Декабрь 2025: {dec_orders} заказов, {dec_2025.get('revenue', 0):,.0f} ₽")
    print(f"Февраль 2026: {feb_orders} заказов, {feb_2026.get('revenue', 0):,.0f} ₽")
    print(f"\n⚠️ ПАДЕНИЕ: {abs(drop_percent):.1f}%")
    
    if drop_percent < -40:
        print(f"🔴 КРИТИЧНО: Падение более 40%!")

# ===== АНАЛИЗ ТОПОВЫХ ТОВАРОВ =====
print(f"\n🏆 АНАЛИЗ ПРОДАЖ ПО ТОВАРАМ")
print("─" * 70)

# Группировка по артикулам
product_sales = defaultdict(lambda: {'revenue': 0, 'orders': 0, 'last_sale': None})

for sale in sales_data:
    nm_id = sale.get('nmId')
    if nm_id:
        product_sales[nm_id]['revenue'] += sale.get('finishedPrice', 0)
        product_sales[nm_id]['orders'] += 1
        
        sale_date = sale.get('date')
        if sale_date:
            if not product_sales[nm_id]['last_sale'] or sale_date > product_sales[nm_id]['last_sale']:
                product_sales[nm_id]['last_sale'] = sale_date

# Топ-10 по выручке
top_products = sorted(product_sales.items(), key=lambda x: x[1]['revenue'], reverse=True)[:10]

print("\nТОП-10 товаров по выручке:")
print(f"{'NM_ID':<12} {'Заказов':>10} {'Выручка (₽)':>15} {'Последняя продажа':<20}")
print("─" * 70)

inactive_products = []
for nm_id, data in top_products:
    last_sale = data['last_sale'][:10] if data['last_sale'] else 'Нет данных'
    print(f"{nm_id:<12} {data['orders']:>10} {data['revenue']:>15,.0f} {last_sale:<20}")
    
    # Проверка активности
    if data['last_sale']:
        last_date = datetime.fromisoformat(data['last_sale'].replace('Z', '+00:00'))
        days_since = (datetime.now(last_date.tzinfo) - last_date).days
        if days_since > 30:
            inactive_products.append((nm_id, days_since))

# ===== АНАЛИЗ ОСТАТКОВ =====
print(f"\n📦 АНАЛИЗ ОСТАТКОВ")
print("─" * 70)

# Группировка остатков по товарам
stock_by_product = defaultdict(int)
for stock in stocks_data:
    nm_id = stock.get('nmId')
    qty = stock.get('quantity', 0)
    if nm_id:
        stock_by_product[nm_id] += qty

zero_stock = {nm for nm, qty in stock_by_product.items() if qty == 0}
low_stock = {nm for nm, qty in stock_by_product.items() if 0 < qty < 5}

print(f"Товаров с нулевым остатком: {len(zero_stock)}")
print(f"Товаров с низким остатком (<5): {len(low_stock)}")

# Проверка топовых товаров на остатки
print(f"\nПроверка остатков топовых товаров:")
for nm_id, data in top_products[:5]:
    stock = stock_by_product.get(nm_id, 0)
    status = "✓" if stock > 10 else ("⚠️" if stock > 0 else "❌")
    print(f"  {status} NM_{nm_id}: {stock} шт в наличии")

# ===== ПРИЧИНЫ УПАДКА =====
print(f"\n🔍 ВЫЯВЛЕННЫЕ ПРИЧИНЫ УПАДКА")
print("─" * 70)

causes = []

# 1. Сезонность
causes.append({
    'reason': 'СЕЗОННОСТЬ',
    'severity': '🟡 СРЕДНЯЯ',
    'description': 'Декабрь - новогодний пик (533 заказа), январь-февраль - сезонный спад',
    'impact': '~50% падения',
    'solution': 'Ожидаемо, но нужна работа над внесезонными позициями'
})

# 2. Нулевые остатки
if len(zero_stock) > len(stock_by_product) * 0.2:
    causes.append({
        'reason': 'НУЛЕВЫЕ ОСТАТКИ',
        'severity': '🔴 КРИТИЧЕСКАЯ',
        'description': f'{len(zero_stock)} товаров без остатков - продажи невозможны',
        'impact': f'~{(len(zero_stock)/len(stock_by_product)*100):.0f}% каталога не продается',
        'solution': 'СРОЧНО: Пополнить остатки популярных позиций'
    })

# 3. Неактивные товары
if inactive_products:
    causes.append({
        'reason': 'НЕАКТИВНЫЕ ТОПОВЫЕ ТОВАРЫ',
        'severity': '🔴 КРИТИЧЕСКАЯ',
        'description': f'{len(inactive_products)} топовых товаров не продавались >30 дней',
        'impact': 'Потеря продаж по прибыльным позициям',
        'solution': 'Проверить остатки, цены, видимость в поиске'
    })

# 4. Незаполненные карточки
incomplete = report['summary']['incomplete_cards']
if incomplete > 50:
    causes.append({
        'reason': 'НЕЗАПОЛНЕННЫЕ КАРТОЧКИ',
        'severity': '🟡 СРЕДНЯЯ',
        'description': f'{incomplete} карточек с неполной информацией',
        'impact': 'Низкая конверсия, плохие позиции в поиске',
        'solution': 'Завершить SEO оптимизацию всех карточек'
    })

# Вывод причин
for i, cause in enumerate(causes, 1):
    print(f"\n{i}. {cause['reason']} - {cause['severity']}")
    print(f"   Описание: {cause['description']}")
    print(f"   Влияние: {cause['impact']}")
    print(f"   Решение: {cause['solution']}")

# ===== ПЛАН ВОССТАНОВЛЕНИЯ =====
print(f"\n{'='*70}")
print("🚀 ПЛАН ВОССТАНОВЛЕНИЯ ПРОДАЖ")
print(f"{'='*70}")

recovery_plan = [
    {
        'priority': '🔴 КРИТИЧНО',
        'action': 'Пополнить остатки',
        'details': f'Пополнить {len(zero_stock)} товаров с нулевым остатком',
        'deadline': 'Немедленно',
        'expected_effect': '+30-40% продаж'
    },
    {
        'priority': '🔴 КРИТИЧНО',
        'action': 'Реанимировать топовые товары',
        'details': f'Проверить {len(inactive_products)} неактивных топовых позиций',
        'deadline': '1-2 дня',
        'expected_effect': '+20-30% продаж'
    },
    {
        'priority': '🟡 ВАЖНО',
        'action': 'Завершить SEO оптимизацию',
        'details': f'Оптимизировать {incomplete} незаполненных карточек',
        'deadline': '1 неделя',
        'expected_effect': '+15-25% конверсия'
    },
    {
        'priority': '🟡 ВАЖНО',
        'action': 'Запустить рекламу',
        'details': 'Рекламные кампании на топовые позиции + сезонные предложения',
        'deadline': '3-5 дней',
        'expected_effect': '+20-40% видимость'
    },
    {
        'priority': '🟢 СРЕДНЕ',
        'action': 'Расширить ассортимент',
        'details': 'Добавить внесезонные позиции для стабилизации продаж',
        'deadline': '2-4 недели',
        'expected_effect': 'Стабилизация продаж'
    }
]

for i, task in enumerate(recovery_plan, 1):
    print(f"\n{task['priority']} ЭТАП {i}: {task['action']}")
    print(f"   Детали: {task['details']}")
    print(f"   Срок: {task['deadline']}")
    print(f"   Эффект: {task['expected_effect']}")

# Сохранение плана
recovery_report = {
    'generated_at': datetime.now().isoformat(),
    'current_status': {
        'monthly_orders': feb_orders,
        'monthly_revenue': feb_2026.get('revenue', 0),
        'drop_from_peak': f'{abs(drop_percent):.1f}%' if 'drop_percent' in locals() else 'N/A'
    },
    'causes': causes,
    'recovery_plan': recovery_plan,
    'top_products': [
        {'nm_id': nm, 'revenue': data['revenue'], 'orders': data['orders']}
        for nm, data in top_products
    ],
    'zero_stock_items': list(zero_stock)[:100],
    'inactive_items': [{'nm_id': nm, 'days_inactive': days} for nm, days in inactive_products]
}

with open(os.path.join(ANALYTICS_DIR, 'wb_recovery_plan.json'), 'w', encoding='utf-8') as f:
    json.dump(recovery_report, f, ensure_ascii=False, indent=2)

print(f"\n{'='*70}")
print("✓ Полный план восстановления сохранен:")
print(f"  {os.path.join(ANALYTICS_DIR, 'wb_recovery_plan.json')}")
print(f"{'='*70}\n")
