# -*- coding: utf-8 -*-
"""
АНАЛИЗ ПРОДАЖ WILDBERRIES ЗА ГОД
Сравнение с прошлым периодом и выявление причин упадка
"""
import json
import os
import requests
from datetime import datetime, timedelta
from collections import defaultdict

BASE_DIR = r'C:\Users\GravMix\.gemini\antigravity\playground\core-pulsar'
ENV_PATH = os.path.join(BASE_DIR, '.env')

# Загрузка API ключа
WB_KEY = ''
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('WB_API_KEY='):
                WB_KEY = line.strip().split('=', 1)[1]
                break

if not WB_KEY:
    print("❌ WB_API_KEY not found")
    exit(1)

headers = {'Authorization': WB_KEY}

print("╔══════════════════════════════════════════════════════════════╗")
print("║           АНАЛИЗ ПРОДАЖ WILDBERRIES ЗА ГОД                   ║")
print("╚══════════════════════════════════════════════════════════════╝\n")

# Даты для анализа
today = datetime.now()
year_ago = today - timedelta(days=365)

# Текущий период (последние 30 дней)
current_period_start = today - timedelta(days=30)

# Прошлый год, тот же период
last_year_start = current_period_start - timedelta(days=365)
last_year_end = today - timedelta(days=365)

print(f"📊 Периоды анализа:")
print(f"  Текущий период: {current_period_start.strftime('%d.%m.%Y')} - {today.strftime('%d.%m.%Y')}")
print(f"  Прошлый год: {last_year_start.strftime('%d.%m.%Y')} - {last_year_end.strftime('%d.%m.%Y')}")
print()

# API endpoint для статистики заказов и продаж
stats_url = 'https://statistics-api.wildberries.ru/api/v1/supplier/sales'

# Параметры для текущего периода
params_current = {
    'dateFrom': current_period_start.strftime('%Y-%m-%d')
}

# Параметры для прошлого года
params_last_year = {
    'dateFrom': last_year_start.strftime('%Y-%m-%d'),
    'dateTo': last_year_end.strftime('%Y-%m-%d')
}

stats_current = []
stats_last_year = []

print("🔍 Загрузка статистики продаж...")

# Получаем текущую статистику
try:
    r = requests.get(stats_url, headers=headers, params=params_current, timeout=30)
    if r.status_code == 200:
        stats_current = r.json()
        print(f"  ✓ Текущий период: {len(stats_current)} записей")
    else:
        print(f"  ❌ Ошибка текущего периода: {r.status_code}")
except Exception as e:
    print(f"  ❌ Exception текущий: {e}")

# Получаем прошлогоднюю статистику
try:
    r = requests.get(stats_url, headers=headers, params=params_last_year, timeout=30)
    if r.status_code == 200:
        stats_last_year = r.json()
        print(f"  ✓ Прошлый год: {len(stats_last_year)} записей")
    else:
        print(f"  ❌ Ошибка прошлого года: {r.status_code}")
except Exception as e:
    print(f"  ❌ Exception прошлый год: {e}")

print()

# Анализ данных
if stats_current or stats_last_year:
    analysis = {
        'current': {
            'total_sales': 0,
            'total_revenue': 0,
            'total_items': 0,
            'avg_price': 0,
            'top_products': defaultdict(int),
            'cancelled': 0
        },
        'last_year': {
            'total_sales': 0,
            'total_revenue': 0,
            'total_items': 0,
            'avg_price': 0,
            'top_products': defaultdict(int),
            'cancelled': 0
        }
    }
    
    # Анализ текущего периода
    for sale in stats_current:
        if sale.get('saleID'):  # Продажа
            analysis['current']['total_sales'] += 1
            analysis['current']['total_revenue'] += sale.get('finishedPrice', 0)
            analysis['current']['total_items'] += 1
            
            nm_id = sale.get('nmId')
            if nm_id:
                analysis['current']['top_products'][nm_id] += 1
        
        if sale.get('saleID') and sale.get('saleID').startswith('C'):  # Отмена
            analysis['current']['cancelled'] += 1
    
    # Анализ прошлого года
    for sale in stats_last_year:
        if sale.get('saleID'):
            analysis['last_year']['total_sales'] += 1
            analysis['last_year']['total_revenue'] += sale.get('finishedPrice', 0)
            analysis['last_year']['total_items'] += 1
            
            nm_id = sale.get('nmId')
            if nm_id:
                analysis['last_year']['top_products'][nm_id] += 1
        
        if sale.get('saleID') and sale.get('saleID').startswith('C'):
            analysis['last_year']['cancelled'] += 1
    
    # Средние цены
    if analysis['current']['total_items'] > 0:
        analysis['current']['avg_price'] = analysis['current']['total_revenue'] / analysis['current']['total_items']
    
    if analysis['last_year']['total_items'] > 0:
        analysis['last_year']['avg_price'] = analysis['last_year']['total_revenue'] / analysis['last_year']['total_items']
    
    # Вывод результатов
    print("=" * 60)
    print("📊 СРАВНИТЕЛЬНАЯ СТАТИСТИКА")
    print("=" * 60)
    
    print(f"\n{'Метрика':<30} {'Текущий период':<20} {'Прошлый год':<20}")
    print("-" * 70)
    
    print(f"{'Продажи (шт)':<30} {analysis['current']['total_sales']:<20} {analysis['last_year']['total_sales']:<20}")
    print(f"{'Выручка (руб)':<30} {analysis['current']['total_revenue']:<20.2f} {analysis['last_year']['total_revenue']:<20.2f}")
    print(f"{'Средний чек (руб)':<30} {analysis['current']['avg_price']:<20.2f} {analysis['last_year']['avg_price']:<20.2f}")
    print(f"{'Отмены':<30} {analysis['current']['cancelled']:<20} {analysis['last_year']['cancelled']:<20}")
    
    # Расчет изменений
    if analysis['last_year']['total_sales'] > 0:
        sales_change = ((analysis['current']['total_sales'] - analysis['last_year']['total_sales']) / 
                       analysis['last_year']['total_sales'] * 100)
        revenue_change = ((analysis['current']['total_revenue'] - analysis['last_year']['total_revenue']) / 
                         analysis['last_year']['total_revenue'] * 100)
        
        print(f"\n{'ИЗМЕНЕНИЯ:':<30}")
        print(f"{'Продажи':<30} {sales_change:+.1f}%")
        print(f"{'Выручка':<30} {revenue_change:+.1f}%")
    
    # Топ-5 продуктов текущего периода
    print(f"\n{'ТОП-5 ПРОДУКТОВ (текущий период):':<30}")
    top_current = sorted(analysis['current']['top_products'].items(), key=lambda x: x[1], reverse=True)[:5]
    for nm_id, count in top_current:
        print(f"  NM_{nm_id}: {count} продаж")
    
    # Сохранение результатов
    with open(os.path.join(BASE_DIR, 'wb_sales_analysis.json'), 'w', encoding='utf-8') as f:
        json.dump({
            'analysis': {
                'current': {k: v if not isinstance(v, defaultdict) else dict(v) 
                           for k, v in analysis['current'].items()},
                'last_year': {k: v if not isinstance(v, defaultdict) else dict(v) 
                             for k, v in analysis['last_year'].items()}
            },
            'raw_current': stats_current[:100],  # Первые 100 для анализа
            'raw_last_year': stats_last_year[:100]
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Детальный анализ сохранен: wb_sales_analysis.json")

else:
    print("⚠ Недостаточно данных для анализа")
