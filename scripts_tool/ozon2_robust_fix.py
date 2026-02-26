import requests
import json
import time

H = {
    'Client-Id': '311191',
    'Api-Key': '88da03d6-8f00-4189-af6b-db145ec7689f',
    'Content-Type': 'application/json'
}

def final_robust_fix():
    print("Fetching active items list...")
    r = requests.post('https://api-seller.ozon.ru/v3/product/list', headers=H, json={'filter': {'visibility': 'ALL'}, 'limit': 1000})
    items = r.json().get('result', {}).get('items', [])
    
    # Target OIDs for collision fix
    targets = ['17272vagner', '123123vagner', 'брел13']
    
    for oid in targets:
        match = [it for it in items if it['offer_id'].lower() == oid.lower()]
        if not match:
            print(f"Product {oid} not found.")
            continue
            
        pid = match[0]['product_id']
        actual_oid = match[0]['offer_id']
        print(f"Processing {actual_oid} (PID: {pid})...")
        
        # Get category and type via v3/product/info/list
        r_info = requests.post('https://api-seller.ozon.ru/v3/product/info/list', headers=H, json={'product_id': [pid]})
        info_data = r_info.json().get('result', {}).get('items', [])
        if not info_data:
            print(f"  Failed to get info for {actual_oid}")
            continue
            
        it_info = info_data[0]
        cat_id = it_info.get('description_category_id')
        type_id = it_info.get('type_id')
        
        # Determine unique attributes
        new_model = "Жетон с гравировкой GRAVMIX"
        new_color = "Индивидуальный (v2)" if "17272" in actual_oid else "Индивидуальный"
        if actual_oid == "брел13": new_color = "Брелок с гравировкой"
        
        print(f"  Updating {actual_oid} -> Model: '{new_model}', Color Name: '{new_color}'")
        
        payload = {
            'items': [{
                'offer_id': actual_oid,
                'description_category_id': cat_id,
                'type_id': type_id,
                'attributes': [
                    {'id': 9048, 'values': [{'value': new_model}]},
                    {'id': 10097, 'values': [{'value': new_color}]}
                ]
            }]
        }
        
        r_upd = requests.post('https://api-seller.ozon.ru/v1/product/attributes/update', headers=H, json=payload)
        print(f"  Result: {r_upd.status_code}")
        time.sleep(1)

if __name__ == "__main__":
    final_robust_fix()
