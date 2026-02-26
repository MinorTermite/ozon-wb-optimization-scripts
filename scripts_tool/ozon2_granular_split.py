import requests
import json
import time
import re

H = {
    'Client-Id': '311191',
    'Api-Key': '88da03d6-8f00-4189-af6b-db145ec7689f',
    'Content-Type': 'application/json'
}

def get_model_name(title):
    t = title.lower()
    if any(k in t for k in ["жетон", "вагнер", "вдв", "погран", "спецназ"]): return "Армейские жетоны GRAVMIX"
    if any(k in t for k in ["овен", "телец", "близнецы", "рак", "лев", "дева", "весы", "скорпион", "стрелец", "козерог", "водолей", "рыбы", "зодиак"]): return "Браслет Знаки Зодиака GRAVMIX"
    if any(k in t for k in ["маме", "мамы", "мама", "папе", "папа", "бабушке", "дедушке", "родителям"]): return "Браслет Подарки Семье GRAVMIX"
    if any(k in t for k in ["сыну", "дочери", "дочке", "ребенку", "детям"]): return "Браслет Подарки Детям GRAVMIX"
    if any(k in t for k in ["люблю", "love", "влюбленных", "парные", "половинке"]): return "Браслеты для Влюбленных GRAVMIX"
    if any(k in t for k in ["молитва", "отче наш", "псалом 90", "спаси и сохрани", "бог", "аллах"]): return "Браслеты Молитвы GRAVMIX"
    if any(k in t for k in ["оберег", "красная нить", "талисман"]): return "Браслеты Обереги GRAVMIX"
    if any(k in t for k in ["цитата", "надписью", "смыслом", "carpe diem", "никогда не сдавайся"]): return "Браслеты с надписью GRAVMIX"
    return "Браслеты с гравировкой GRAVMIX"

def granular_split():
    print("Fetching active products list...")
    r_list = requests.post('https://api-seller.ozon.ru/v3/product/list', headers=H, json={'filter': {'visibility': 'IN_SALE'}, 'limit': 1000})
    pids = [it['product_id'] for it in r_list.json().get('result', {}).get('items', [])]
    
    print(f"Fetching attributes for {len(pids)} items...")
    all_attrs = []
    for i in range(0, len(pids), 50):
        batch = pids[i:i+50]
        r_at = requests.post('https://api-seller.ozon.ru/v4/product/info/attributes', headers=H, json={'filter': {'product_id': batch}, 'limit': 50})
        all_attrs.extend(r_at.json().get('result', []))

    updates = []
    stats = {}
    
    for item in all_attrs:
        pid = item['product_id']
        oid = item['offer_id']
        
        # Get current title
        title = ""
        for a in item['attributes']:
            if a['id'] == 4180: # Название товара
                title = a['values'][0]['value']
                break
        
        if not title: # try 4191
             for a in item['attributes']:
                if a['id'] == 4191:
                    title = a['values'][0]['value']
                    break
        
        new_model_name = get_model_name(title)
        stats[new_model_name] = stats.get(new_model_name, 0) + 1
        
        updates.append({
            "offer_id": oid,
            "attributes": [
                {
                    "id": 9048, # Model Name
                    "values": [{"value": new_model_name}]
                }
            ]
        })

    print("\nProposed Statistics:")
    for m, count in stats.items():
        print(f" - {m}: {count} items")

    print(f"\nApplying updates for {len(updates)} items...")
    for i in range(0, len(updates), 50):
        batch = updates[i:i+50]
        r_up = requests.post('https://api-seller.ozon.ru/v1/product/attributes/update', headers=H, json={'items': batch})
        if r_up.status_code == 200:
            print(f"  Batch {i//50 + 1} Success")
        else:
            print(f"  Batch {i//50 + 1} Error: {r_up.text[:200]}")
        time.sleep(1)

    print("\nGRANULAR SPLIT COMPLETE.")

if __name__ == "__main__":
    granular_split()
