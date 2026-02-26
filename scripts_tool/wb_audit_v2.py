# -*- coding: utf-8 -*-
"""
WB Data Export for Unit Economics and Ad Audit - Fix List Request
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

print("\nFetching Ad Campaigns from WB...")

# The endpoint /adv/v1/promotion/adverts expects an array of ints, not an object. Wait, it's for get by IDs.
# For list of campaigns, the endpoint might be /adv/v1/promotion/count (GET)
# Let's get the count and IDs first

r_count = requests.get('https://advert-api.wildberries.ru/adv/v1/promotion/count', headers=H)
if r_count.status_code == 200:
    count_data = r_count.json()
    print(f"Count data: {json.dumps(count_data, ensure_ascii=False)}")
    
    ad_ids = []
    # Collect all IDs
    adverts = count_data.get("adverts", [])
    if isinstance(adverts, list):
         for type_group in adverts:
             if type_group.get("status") in [9, 11]:  # Active or Paused
                  # 'advert_list' contains objects with 'advertId'
                  for ad in type_group.get("advert_list", []):
                       ad_ids.append(ad.get("advertId"))
    
    print(f"Total active/paused ad IDs extracted: {len(ad_ids)}")
    
    camp_details = []
    if ad_ids:
         # Now get details by IDs (max 50 per request)
         for i in range(0, len(ad_ids), 50):
             batch = ad_ids[i:i+50]
             r_info = requests.post('https://advert-api.wildberries.ru/adv/v1/promotion/adverts', headers=H, json=batch)
             if r_info.status_code == 200:
                  camps = r_info.json()
                  # Extract name and type
                  for c in camps:
                       camp_details.append({
                           "id": c.get("advertId"),
                           "name": c.get("name"),
                           "type": c.get("type"),
                           "status": c.get("status")
                       })
             else:
                  print(f"Error fetching batch {batch}: {r_info.status_code} {r_info.text}")
    
    # Now get budgets
    for c in camp_details:
        cid = c["id"]
        r_budget = requests.get(f'https://advert-api.wildberries.ru/adv/v1/budget?id={cid}', headers=H)
        if r_budget.status_code == 200:
             c["budget"] = r_budget.json().get("total")
        
        # Depending on type (8=auto, 9=search), get CPM
        cpm_url = f'https://advert-api.wildberries.ru/adv/v1/auto/stat?id={cid}' if c["type"] == 8 else f'https://advert-api.wildberries.ru/adv/v1/search/stat?id={cid}'
        r_cpm = requests.get(cpm_url, headers=H)
        if r_cpm.status_code == 200:
             c["cpm"] = r_cpm.json().get("cpm", 0)
        
        # State
        state_str = "ACTIVE" if c["status"] == 9 else "PAUSED"
        print(f"[{state_str}] {c['name'][:30]:30s} ID:{cid:<10} Type:{c['type']} Budget:{c.get('budget','?')} RUB")

else:
    print(f"Error fetching count: {r_count.status_code} {r_count.text}")
