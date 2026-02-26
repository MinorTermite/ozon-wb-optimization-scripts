import requests
import json
import time

H = {
    'Client-Id': '311191',
    'Api-Key': '88da03d6-8f00-4189-af6b-db145ec7689f',
    'Content-Type': 'application/json'
}

def definitive_fix():
    print("Step 1: Fetching target products (Vagner and Clashes)...")
    r = requests.post('https://api-seller.ozon.ru/v3/product/list', headers=H, json={'filter': {'visibility': 'ALL'}, 'limit': 1000})
    items = r.json().get('result', {}).get('items', [])
    
    # 17272vagner, 123123vagner, and anything that might be 'брел13' 
    vagner_matches = [it for it in items if 'vagner' in it['offer_id'].lower()]
    brelok_matches = [it for it in items if '13' in it['offer_id'] and len(it['offer_id']) < 10]
    
    targets = vagner_matches + brelok_matches
    print(f"Found {len(targets)} targets to fix.")

    for it in targets:
        oid = it['offer_id']
        pid = it['product_id']
        print(f"\nProcessing {oid} (PID: {pid})...")
        
        # Pull attributes via v3 info/list (more reliable for JSON)
        r_info = requests.post('https://api-seller.ozon.ru/v3/product/info/list', headers=H, json={'product_id': [pid]})
        info_list = r_info.json().get('result', {}).get('items', [])
        if not info_list:
            print(f"  FAILED to get info for {oid}")
            continue
            
        info = info_list[0]
        cat_id = info.get('description_category_id')
        type_id = info.get('type_id')
        
        # Fix logic: Move Vagner to its own model, unique colors for all
        new_model = "Жетон с гравировкой GRAVMIX"
        new_color = "Индивидуальный"
        if "17272" in oid: new_color = "Вагнер тип 2"
        elif "123123" in oid: new_color = "Вагнер тип 1"
        elif "13" in oid: new_color = "Брелок с гравировкой"

        print(f"  Action: Model='{new_model}', Color='{new_color}'")
        
        payload = {
            'items': [{
                'offer_id': oid,
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
    definitive_fix()
