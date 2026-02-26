import requests
import json
import time
from collections import defaultdict

H = {
    'Client-Id': '311191',
    'Api-Key': '88da03d6-8f00-4189-af6b-db145ec7689f',
    'Content-Type': 'application/json'
}

def audit_collisions():
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
        else:
            print(f"  Batch failed: {r.status_code}")
        time.sleep(1)

    # Grouping logic
    # Key: Model Name (Attr 9048)
    # Subkey: (Color Attr 10096, Color Name Attr 10097)
    models = defaultdict(lambda: defaultdict(list))
    
    for item in all_details:
        oid = item.get('offer_id')
        name = item.get('name')
        
        model_name = ""
        color_id = 0
        color_name = ""
        
        for a in item.get('attributes', []):
            aid = a.get('id')
            if aid == 9048:
                model_name = a.get('values')[0].get('value') if a.get('values') else ""
            elif aid == 10096:
                color_id = a.get('values')[0].get('dictionary_value_id') if a.get('values') else 0
            elif aid == 10097:
                color_name = a.get('values')[0].get('value') if a.get('values') else ""

        if model_name:
            variant_key = (color_id, color_name)
            models[model_name][variant_key].append(oid)

    print("\n--- COLLISION REPORT ---")
    collisions_found = False
    for model, variants in models.items():
        for vkey, skus in variants.items():
            if len(skus) > 1:
                print(f"Collision in Model '{model}':")
                print(f"  Variant Attributes: ColorID={vkey[0]}, ColorName='{vkey[1]}'")
                print(f"  Affected SKUs: {skus}")
                collisions_found = True
    
    if not collisions_found:
        print("No attribute collisions found among 130 products.")

if __name__ == "__main__":
    audit_collisions()
