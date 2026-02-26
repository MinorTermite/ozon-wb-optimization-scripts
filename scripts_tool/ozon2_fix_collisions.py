import requests
import json
import time
from collections import defaultdict

H = {
    'Client-Id': '311191',
    'Api-Key': '88da03d6-8f00-4189-af6b-db145ec7689f',
    'Content-Type': 'application/json'
}

def fix_collisions():
    print("Loading active 130 products...")
    with open('ozon2_active_130.json', 'r', encoding='utf-8') as f:
        products = json.load(f)

    pids = [p['id'] for p in products]
    
    print(f"Fetching attributes for {len(pids)} products...")
    all_details = []
    for i in range(0, len(pids), 50):
        batch = pids[i:i+50]
        r = requests.post('https://api-seller.ozon.ru/v4/product/info/attributes', headers=H, json={'filter': {'product_id': batch}, 'limit': 50})
        if r.status_code == 200:
            all_details.extend(r.json().get('result', []))
        time.sleep(1)

    # Dictionary to track variations within models
    # model -> (color_id, color_name) -> count
    model_variants = defaultdict(lambda: defaultdict(int))
    
    updates = []
    for item in all_details:
        oid = item.get('offer_id')
        cat_id = item.get('description_category_id')
        type_id = item.get('type_id')
        
        model_name = ""
        color_id = 0
        color_name = ""
        
        # Extract current variant attributes
        for a in item.get('attributes', []):
            aid = a.get('id')
            if aid == 9048:
                model_name = a.get('values')[0].get('value') if a.get('values') else ""
            elif aid == 10096:
                color_id = a.get('values')[0].get('dictionary_value_id') if a.get('values') else 0
            elif aid == 10097:
                color_name = a.get('values')[0].get('value') if a.get('values') else ""

        if not model_name:
            continue
            
        v_key = (color_id, color_name)
        model_variants[model_name][v_key] += 1
        
        # If this is a collision (count > 1), we need to modify color_name
        if model_variants[model_name][v_key] > 1:
            # Generate a unique color name
            # If SKU has '2' in it, use 'Тип 2' or similar
            suffix = f" тип {model_variants[model_name][v_key]}"
            if "2" in oid:
                suffix = " тип 2"
            
            new_color_name = color_name if color_name else "Индивидуальный"
            new_color_name += suffix
            
            print(f"Fixing collision for {oid}: '{color_name}' -> '{new_color_name}'")
            
            updates.append({
                "description_category_id": cat_id,
                "type_id": type_id,
                "offer_id": oid,
                "attributes": [
                    {"id": 10097, "values": [{"value": new_color_name}]}
                ]
            })

    if not updates:
        print("No collisions to fix.")
        return

    print(f"Applying {len(updates)} fixes...")
    BATCH_SIZE = 10
    for i in range(0, len(updates), BATCH_SIZE):
        batch = updates[i:i+BATCH_SIZE]
        r = requests.post("https://api-seller.ozon.ru/v1/product/attributes/update", headers=H, json={"items": batch})
        if r.status_code == 200:
            print(f"  Processed {i+len(batch)}/{len(updates)}")
        else:
            print(f"  Error at {i}: {r.status_code} {r.text[:200]}")
        time.sleep(1)

if __name__ == "__main__":
    fix_collisions()
