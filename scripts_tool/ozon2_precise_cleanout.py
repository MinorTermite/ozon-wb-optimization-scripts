import requests
import json
import time
from typing import List, Dict, Any

H = {
    'Client-Id': '311191',
    'Api-Key': '88da03d6-8f00-4189-af6b-db145ec7689f',
    'Content-Type': 'application/json'
}

def precise_cleanout():
    print("Fetching items in the current 'heap' (Браслеты с гравировкой GRAVMIX)...")
    r_list = requests.post('https://api-seller.ozon.ru/v3/product/list', headers=H, json={'filter': {'visibility': 'IN_SALE'}, 'limit': 1000})
    items: list = r_list.json().get('result', {}).get('items', [])
    pids: list = [it['product_id'] for it in items]
    
    all_attrs = []
    for i in range(0, len(pids), 50):
        batch = pids[i:i+50]
        r_at = requests.post('https://api-seller.ozon.ru/v4/product/info/attributes', headers=H, json={'filter': {'product_id': batch}, 'limit': 50})
        all_attrs.extend(r_at.json().get('result', []))

    heap_items = []
    for res in all_attrs:
        m_name = next((a['values'][0]['value'] for a in res['attributes'] if a['id'] == 9048), 'N')
        if m_name == 'Браслеты с гравировкой GRAVMIX':
            heap_items.append(res)

    print(f"Found {len(heap_items)} items to re-classify.")
    
    updates: list = []
    for item in heap_items:
        oid = item.get('offer_id')
        title = ""
        for a in item['attributes']:
            if a['id'] == 4180: title = a['values'][0]['value']
            elif a['id'] == 4191 and not title: title = a['values'][0]['value']
        
        t = str(title).lower()
        new_name = None
        
        # Family Re-check (More aggressive keywords)
        if any(k in t for k in ["мама", "папа", "бабуш", "дедуш", "родител", "семье", "маме", "папе", "любимой маме", "лучшей маме"]):
            new_name = "Браслет Подарки Семье GRAVMIX"
        # Children Re-check
        elif any(k in t for k in ["сын", "доч", "реben", "детям", "любимому сыну", "любимой доче"]):
            new_name = "Браслет Подарки Детям GRAVMIX"
        # Zodiac Re-check
        elif any(k in t for k in ["овен", "телец", "близнец", "рак", "лев", "дева", "весы", "скорпион", "стрелец", "козерог", "водолей", "рыбы", "зодиак"]):
            new_name = "Браслет Знаки Зодиака GRAVMIX"
        # Army/Jeton Re-check
        elif any(k in t for k in ["жетон", "армей", "вагнер", "вдв", "погран", "спецназ", "войск"]):
            new_name = "Армейские жетоны GRAVMIX"
        # Love/Pairs
        elif any(k in t for k in ["люблю", "love", "влюблен", "парн", "половинк", "вместе", "всегда рядом"]):
            new_name = "Браслеты для Влюбленных GRAVMIX"
        # Religion
        elif any(k in t for k in ["молитв", "отче наш", "псалом 90", "спаси и сохрани", "бог", "аллах", "иисус"]):
            new_name = "Браслеты Молитвы GRAVMIX"
            
        if new_name:
            print(f"  Re-classifying {oid} -> {new_name} (Title: {title[:50]})")
            updates.append({
                "offer_id": oid,
                "attributes": [{"id": 9048, "complex_id": 0, "values": [{"value": new_name}]}]
            })

    if updates:
        print(f"Applying {len(updates)} precise updates...")
        for i in range(0, len(updates), 50):
            batch = updates[i:i+50]
            r_up = requests.post('https://api-seller.ozon.ru/v1/product/attributes/update', headers=H, json={'items': batch})
            print(f"  Batch {i//50 + 1}: {r_up.status_code}")
        time.sleep(1)
    else:
        print("No further simple re-classifictions found. Remaining items are likely unique or generic.")

if __name__ == "__main__":
    precise_cleanout()
