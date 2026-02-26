import requests
import json
import time

H = {
    'Client-Id': '311191',
    'Api-Key': '88da03d6-8f00-4189-af6b-db145ec7689f',
    'Content-Type': 'application/json'
}

def fix_last_clash():
    print("Searching for target products...")
    r = requests.post('https://api-seller.ozon.ru/v3/product/list', headers=H, json={'filter': {'visibility': 'ALL'}, 'limit': 1000})
    items = r.json().get('result', {}).get('items', [])
    
    # Target SKUs that might be causing the collision in "Жетон Знаки Зодиака GRAVMIX"
    target_oids = ['17272vagner', '123123vagner', 'брел13']
    
    for oid_to_match in target_oids:
        match = [it for it in items if it['offer_id'].lower() == oid_to_match.lower()]
        if not match:
            print(f"Product {oid_to_match} not found.")
            continue

        it = match[0]
        pid = it['product_id']
        oid = it['offer_id']
        print(f"\nProcessing: {oid} (PID: {pid})")
        
        # Get attributes via v3 info/list if v4 fails or to be safe
        r_info = requests.post('https://api-seller.ozon.ru/v3/product/info/list', headers=H, json={'product_id': [pid]})
        info_list = r_info.json().get('result', {}).get('items', [])
        if not info_list:
            print(f"  Could not get info for {oid}")
            continue
        
        info = info_list[0]
        cat_id = info.get('description_category_id')
        type_id = info.get('type_id')
        
        # Determine fix logic
        new_attr_id = 10097 # Color Name
        new_value = ""
        
        if 'vagner' in oid.lower():
            # Change Model Name too to separate from Zodiacs
            # 9048: Model Name
            new_model = "Жетон с гравировкой GRAVMIX"
            r_upd = requests.post('https://api-seller.ozon.ru/v1/product/attributes/update', headers=H, json={
                'items': [{
                    'offer_id': oid,
                    'description_category_id': cat_id,
                    'type_id': type_id,
                    'attributes': [{'id': 9048, 'values': [{'value': new_model}]}]
                }]
            })
            print(f"  Updating Model Name for {oid} to '{new_model}': {r_upd.status_code}")
        
        # Also ensure Color Name is unique if they stay in same group
        if oid == '17272vagner': new_value = "Жетон Вагнер (2)"
        elif oid == '123123vagner': new_value = "Жетон Вагнер (1)"
        elif oid == 'брел13': new_value = "Индивидуальный брелок"
        
        if new_value:
            r_upd = requests.post('https://api-seller.ozon.ru/v1/product/attributes/update', headers=H, json={
                'items': [{
                    'offer_id': oid,
                    'description_category_id': cat_id,
                    'type_id': type_id,
                    'attributes': [{'id': 10097, 'values': [{'value': new_value}]}]
                }]
            })
            print(f"  Updating Color Name for {oid} to '{new_value}': {r_upd.status_code}")
        
        time.sleep(1)

if __name__ == "__main__":
    fix_last_clash()
