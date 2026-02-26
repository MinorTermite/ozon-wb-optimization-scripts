import requests
import json

H = {
    'Client-Id': '311191',
    'Api-Key': '88da03d6-8f00-4189-af6b-db145ec7689f',
    'Content-Type': 'application/json'
}

def fix_last_clash():
    print("Searching for target products...")
    r = requests.post('https://api-seller.ozon.ru/v3/product/list', headers=H, json={'filter': {'visibility': 'ALL'}, 'limit': 1000})
    items = r.json().get('result', {}).get('items', [])
    
    # 17272vagner
    target_oid = '17272vagner'
    match = [it for it in items if it['offer_id'].lower() == target_oid.lower()]
    
    if not match:
        print(f"Product {target_oid} not found in listing.")
        return

    it = match[0]
    pid = it['product_id']
    oid = it['offer_id']
    print(f"Found: {oid} (PID: {pid})")
    
    # Get attributes to obtain category/type IDs
    r_at = requests.post('https://api-seller.ozon.ru/v4/product/info/attributes', headers=H, json={'filter': {'product_id': [pid]}})
    res = r_at.json().get('result', [])[0]
    cat_id = res['description_category_id']
    type_id = res['type_id']
    
    # Change Model Name to separate it from Zodiacs
    new_model = "Жетон с гравировкой GRAVMIX"
    print(f"Moving {oid} to Model: {new_model}")
    
    r_upd = requests.post('https://api-seller.ozon.ru/v1/product/attributes/update', headers=H, json={
        'items': [{
            'offer_id': oid,
            'description_category_id': cat_id,
            'type_id': type_id,
            'attributes': [{'id': 9048, 'values': [{'value': new_model}]}]
        }]
    })
    
    print(f"Update Result: {r_upd.status_code} {r_upd.text}")

if __name__ == "__main__":
    fix_last_clash()
