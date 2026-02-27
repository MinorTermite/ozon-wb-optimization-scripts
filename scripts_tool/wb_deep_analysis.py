# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime
from collections import defaultdict

BASE_DIR = r'c:\Users\GravMix\.gemini\antigravity\playground\core-pulsar'
SALES_FILE = os.path.join(BASE_DIR, 'analytics', 'wb_sales_year.json')
ORDERS_FILE = os.path.join(BASE_DIR, 'analytics', 'wb_orders_year.json')
REPORT_FILE = os.path.join(BASE_DIR, 'wb_deep_sales_analysis_report.md')

def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def run_analysis():
    print("🚀 LOADING DATA...")
    sales = load_json(SALES_FILE)
    orders = load_json(ORDERS_FILE)
    
    print(f"✅ Loaded {len(sales)} sales and {len(orders)} orders.")
    
    # Yearly buckets
    data_2024 = {'revenue': 0, 'sales_count': 0, 'orders_count': 0, 'skus': defaultdict(int)}
    data_2025 = {'revenue': 0, 'sales_count': 0, 'orders_count': 0, 'skus': defaultdict(int)}
    
    # Process Sales
    for s in sales:
        date_str = s.get('date', '')
        if not date_str: continue
        
        year = datetime.fromisoformat(date_str).year
        rev = s.get('finishedPrice', 0)
        sku = s.get('nmId')
        
        if year == 2024:
            data_2024['revenue'] += rev
            data_2024['sales_count'] += 1
            if sku: data_2024['skus'][sku] += rev
        elif year == 2025:
            data_2025['revenue'] += rev
            data_2025['sales_count'] += 1
            if sku: data_2025['skus'][sku] += rev

    # Process Orders
    for o in orders:
        date_str = o.get('date', '')
        if not date_str: continue
        year = datetime.fromisoformat(date_str).year
        if year == 2024:
            data_2024['orders_count'] += 1
        elif year == 2025:
            data_2025['orders_count'] += 1

    # Report Generation
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("# 📊 Deep Year-over-Year Sales Analysis (2024 vs 2025)\n\n")
        
        f.write("## 📈 Key Performance Indicators\n\n")
        f.write(f"| Metric | 2024 | 2025 (to date) | Change (%) |\n")
        f.write(f"| :--- | :--- | :--- | :--- |\n")
        
        def perc(v1, v2):
            if v1 == 0: return "N/A"
            return f"{((v2 - v1) / v1 * 100):+.1f}%"

        f.write(f"| Revenue (₽) | {data_2024['revenue']:,} | {data_2025['revenue']:,} | {perc(data_2024['revenue'], data_2025['revenue'])} |\n")
        f.write(f"| Sales Volume (units) | {data_2024['sales_count']:,} | {data_2025['sales_count']:,} | {perc(data_2024['sales_count'], data_2025['sales_count'])} |\n")
        f.write(f"| Orders Volume (units) | {data_2024['orders_count']:,} | {data_2025['orders_count']:,} | {perc(data_2024['orders_count'], data_2025['orders_count'])} |\n")
        
        # Redemption rate
        rr24 = (data_2024['sales_count'] / data_2024['orders_count'] * 100) if data_2024['orders_count'] > 0 else 0
        rr25 = (data_2025['sales_count'] / data_2025['orders_count'] * 100) if data_2025['orders_count'] > 0 else 0
        f.write(f"| Conversion/Redemption (%) | {rr24:.1f}% | {rr25:.1f}% | {perc(rr24, rr25)} |\n\n")
        
        f.write("## 📉 Top Losing Products (Revenue Drop)\n\n")
        # Find SKUs in 2024 that disappeared or dropped in 2025
        drops = []
        for sku, rev24 in data_2024['skus'].items():
            rev25 = data_2025['skus'].get(sku, 0)
            drops.append((sku, rev24, rev25, rev25 - rev24))
        
        drops = sorted(drops, key=lambda x: x[3])[:10]
        
        f.write("| NM ID | 2024 Revenue | 2025 Revenue | Loss |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        for sku, r24, r25, loss in drops:
            f.write(f"| {sku} | {r24:,} | {r25:,} | **{loss:,}** |\n")

    print(f"✅ Analysis complete. Report saved to: {REPORT_FILE}")

if __name__ == "__main__":
    run_analysis()
