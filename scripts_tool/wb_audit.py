# -*- coding: utf-8 -*-
"""
WB Data Export for Unit Economics and Ad Audit
"""
import os, json, requests
from datetime import datetime, timedelta

env_path = '.env'
WB_KEY = ''
with open(env_path, 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('WB_API_KEY='):
            WB_KEY = line.strip().split('=', 1)[1]
            break

H = {'Authorization': WB_KEY, 'Content-Type': 'application/json'}

# 1. Fetch Sales Data (last 30 days)
date_30d = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
print(f"Fetching sales since {date_30d}...")
r_sales = requests.get(f'https://statistics-api.wildberries.ru/api/v1/supplier/sales?dateFrom={date_30d}', headers=H)

sales_data = r_sales.json() if r_sales.status_code == 200 else []
print(f"Total sales records (30d): {len(sales_data)}")

# Analyze sales for unit economics
total_revenue = 0
total_for_pay = 0
commissions = []
spp_values = []
logistics_costs = []

for sale in sales_data:
    if sale.get("saleID", "").startswith("S"): # Sale (not return "R")
        priceWithDisc = sale.get("priceWithDisc", 0) # What buyer paid BEFORE SPP (often) OR base retail
        finishedPrice = sale.get("finishedPrice", 0) # What buyer actually paid (with WB SPP)
        forPay = sale.get("forPay", 0)               # What seller receives
        
        total_revenue += finishedPrice
        total_for_pay += forPay
        
        # Approximate commission
        # forPay = finishedPrice - WB_Commission - Logistics? Wait, in WB API:
        # forPay is amount to be transferred to seller. WB Commission = priceWithDisc - forPay
        if priceWithDisc > 0 and forPay > 0:
            comm_pct = (priceWithDisc - forPay) / priceWithDisc * 100
            commissions.append(comm_pct)
            
        spp = sale.get("spp", 0)
        if spp > 0: spp_values.append(spp)

# 2. Fetch Orders (to check logistics cost indirectly or just volume)
r_orders = requests.get(f'https://statistics-api.wildberries.ru/api/v1/supplier/orders?dateFrom={date_30d}', headers=H)
orders_data = r_orders.json() if r_orders.status_code == 200 else []
print(f"Total orders (30d): {len(orders_data)}")

# 3. Fetch Ad Campaigns List
print("\nFetching Ad Campaigns...")
r_adv_list = requests.post('https://advert-api.wildberries.ru/adv/v1/promotion/adverts', headers=H, json={
    "status": [9, 11], # 9=Active, 11=Paused
    "type": 8, # AUTO campaigns (Search+Catalog)
    "limit": 50,
    "offset": 0
})

campaigns = []
if r_adv_list.status_code == 200:
    campaigns = r_adv_list.json()
    print(f"Found {len(campaigns)} Auto campaigns")
else:
    print(f"Error fetching campaigns: {r_adv_list.status_code} {r_adv_list.text[:100]}")

# 4. Fetch Ad Configs (Budgets, CPM)
active_camps = [c for c in campaigns if c.get("status") == 9]
camp_details = []

if active_camps:
    print(f"Fetching details for {len(active_camps)} ACTIVE campaigns...")
    c_ids = [c["advertId"] for c in active_camps]
    
    # Needs individual requests or batch depending on WB API version. Standard is via /adv/v1/promotion/adverts but we have them.
    # We need budget information
    # Max array size is usually 50
    for cid in c_ids:
        r_info = requests.get(f'https://advert-api.wildberries.ru/adv/v1/budget?id={cid}', headers=H)
        buf = {"id": cid, "name": next((c["name"] for c in active_camps if c["advertId"] == cid), f"Camp-{cid}")}
        if r_info.status_code == 200:
            buf["budget"] = r_info.json().get("total", 0)
            
        # Try getting daily limits if possible, or CPM
        r_cpm = requests.get(f'https://advert-api.wildberries.ru/adv/v1/auto/stat?id={cid}', headers=H)
        if r_cpm.status_code == 200:
            cpm_data = r_cpm.json()
            buf["cpm"] = cpm_data.get("cpm", 0)
            
        camp_details.append(buf)

# Save dump
wb_dump = {
    "summary": {
        "orders_30d": len(orders_data),
        "sales_30d": len(sales_data),
        "avg_commission_pct": sum(commissions)/len(commissions) if commissions else 0,
        "avg_spp_pct": sum(spp_values)/len(spp_values) if spp_values else 0,
        "total_revenue_30d_rub": total_revenue,
        "total_payout_30d_rub": total_for_pay,
        "avg_ticket": total_revenue/len(sales_data) if sales_data else 0,
        "avg_payout_per_unit": total_for_pay/len(sales_data) if sales_data else 0,
    },
    "campaigns": camp_details
}

with open("wb_audit_data.json", "w", encoding="utf-8") as f:
    json.dump(wb_dump, f, ensure_ascii=False, indent=2)

print("\n-------------------------")
print("WB 30-DAY SUMMARY")
print("-------------------------")
print(f"Orders:      {wb_dump['summary']['orders_30d']}")
print(f"Sales:       {wb_dump['summary']['sales_30d']}")
print(f"Revenue:     {wb_dump['summary']['total_revenue_30d_rub']:,.0f} RUB")
print(f"Payout:      {wb_dump['summary']['total_payout_30d_rub']:,.0f} RUB")
print(f"Avg Ticket:  {wb_dump['summary']['avg_ticket']:,.0f} RUB")
print(f"Avg Payout:  {wb_dump['summary']['avg_payout_per_unit']:,.0f} RUB")
print(f"Avg Comm%:   {wb_dump['summary']['avg_commission_pct']:.1f}%")
print(f"Avg SPP%:    {wb_dump['summary']['avg_spp_pct']:.1f}%")

print("\nACTIVE CAMPAIGNS:")
for c in camp_details:
    print(f"  [{c['id']}] {c['name'][:30]:30s} Budget: {c.get('budget','?')} RUB, CPM: {c.get('cpm','?')}")

print("\nData saved to wb_audit_data.json")
