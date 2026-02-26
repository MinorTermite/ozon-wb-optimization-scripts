import requests
import json

H = {
    'Client-Id': '311191',
    'Api-Key': '88da03d6-8f00-4189-af6b-db145ec7689f',
    'Content-Type': 'application/json'
}

def fix_vagner_collision():
    print("Searching for vagner items...")
    r = requests.post('https://api-seller.ozon.ru/v3/product/list', headers=H, json={'filter': {'visibility': 'ALL'}, 'limit': 1000})
    items = r.json().get('result', {}).get('items', [])
    vagner_matches = [it for it in items if 'vagner' in it['offer_id'].lower()]
    
    print(f"Found {len(vagner_matches)} vagner items.")
    for it in vagner_matches:
        oid = it['offer_id']
        pid = it['product_id']
        print(f"Processing {oid}...")
        
        # Get attributes via v4
        r_at = requests.post('https://api-seller.ozon.ru/v4/product/info/attributes', headers=H, json={'filter': {'product_id': [pid]}})
        res_list = r_at.json().get('result', [])
        if not res_list:
            print(f"  Failed to get attributes for {oid}")
            continue
            
        res = res_list[0]
        cat_id = res['description_category_id']
        type_id = res['type_id']
        
        # New model and color name to avoid zodiac merge
        new_model = "Жетон с гравировкой GRAVMIX"
        new_color = "Вагнер тип 2" if "17272" in oid else "Вагнер"
        
        print(f"  Attempting update for {oid}...")
        r_upd = requests.post('https://api-seller.ozon.ru/v1/product/attributes/update', headers=H, json={
            'items': [{
                'offer_id': oid,
                'description_category_id': cat_id,
                'type_id': type_id,
                'attributes': [
                    {'id': 9048, 'values': [{'value': new_model}]},
                    {'id': 10097, 'values': [{'value': new_color}]}
                ]
            }]
        })
        print(f"  Update result: {r_upd.status_code}")

if __name__ == "__main__":
    fix_vagner_collision()
