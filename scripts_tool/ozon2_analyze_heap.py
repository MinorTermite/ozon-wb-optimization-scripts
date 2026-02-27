import requests
import json
import time
from collections import defaultdict
from typing import List, Dict, Any

H = {
    'Client-Id': '311191',
    'Api-Key': '88da03d6-8f00-4189-af6b-db145ec7689f',
    'Content-Type': 'application/json'
}

def analyze_ozon_heap():
    print("Fetching active products list...")
    r = requests.post('https://api-seller.ozon.ru/v3/product/list', headers=H, json={'filter': {'visibility': 'IN_SALE'}, 'limit': 1000})
    items: Any = r.json().get('result', {}).get('items', [])
    pids: List[int] = [it['product_id'] for it in items]
    
    print(f"Fetching attributes for {len(pids)} products...")
    all_attrs = []
    pids_list = list(pids)
    for i in range(0, len(pids_list), 50):
        # Using list comprehension instead of slice to satisfy IDE linter
        batch = [pids_list[j] for j in range(i, min(i + 50, len(pids_list)))]
        r_at = requests.post('https://api-seller.ozon.ru/v4/product/info/attributes', headers=H, json={'filter': {'product_id': batch}, 'limit': 50})
        all_attrs.extend(r_at.json().get('result', []))

    # Identify the target group (69 items)
    # The user screenshot shows group 4747605602.
    # In Ozon, groups are formed by Model Name (9048) or Combine ID.
    
    group_model = None
    model_map = defaultdict(list)
    for res in all_attrs:
        oid = res['offer_id']
        attrs = res['attributes']
        model = next((a['values'][0]['value'] for a in attrs if a['id'] == 9048), None)
        if model:
            model_map[model].append(res)

    # Find the group with ~69 items
    target_group_res = []
    for model, items_in_group in model_map.items():
        if len(items_in_group) > 50:
            print(f"Found candidate group: '{model}' with {len(items_in_group)} items")
            group_model = model
            target_group_res = items_in_group
            break

    if not target_group_res:
        print("Could not find the 'heap' group automatically.")
        return

    print(f"\nAnalyzing products in group '{group_model}':")
    categories = defaultdict(list)
    
    for item in target_group_res:
        oid = item['offer_id']
        name = ""
        # Find Title
        for a in item['attributes']:
            if a['id'] in [4180, 4191]:
                name = a['values'][0]['value'] if a['values'] else ""
                break
        
        # Heuristic categorization
        cat = "Прочее"
        n_low = str(name).lower()
        if "знак" in n_low or "зодиак" in n_low:
            cat = "Знаки Зодиака"
        elif "сыну" in n_low or "дочери" in n_low or "ребенку" in n_low:
            cat = "Подарки детям (семья)"
        elif "папе" in n_low or "маме" in n_low or "родител" in n_low:
            cat = "Подарки родителям"
        elif "парн" in n_low or "любим" in n_low or "двоих" in n_low:
            cat = "Парные / Для любимых"
        elif "стали" in n_low and "316l" in n_low:
            cat = "Стальные браслеты (тех)"
        
        categories[cat].append({'oid': oid, 'name': name})

    print("\nPROPOSED SPLIT:")
    for cat, items_cat in categories.items():
        preview_all = list(items_cat)
        # Using list comprehension instead of slice to satisfy IDE linter
        preview = [preview_all[j] for j in range(min(3, len(preview_all)))]
        for it in preview:
            print(f"  - {it['oid']}: {it['name']}")
        if len(items) > 3: print("  ...")

    # Save mapping for later use
    with open('ozon2_heap_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    analyze_ozon_heap()
