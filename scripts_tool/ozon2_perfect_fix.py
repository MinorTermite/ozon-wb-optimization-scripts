import requests
import json

H = {
    'Client-Id': '311191',
    'Api-Key': '88da03d6-8f00-4189-af6b-db145ec7689f',
    'Content-Type': 'application/json'
}

def final_perfect_fix():
    print("Fetching vagner items...")
    r = requests.post('https://api-seller.ozon.ru/v3/product/list', headers=H, json={'filter': {'visibility': 'ALL'}, 'limit': 1000})
    items = r.json().get('result', {}).get('items', [])
    vagner_it = [it for it in items if 'vagner' in it['offer_id'].lower()]
    
    print(f"Applying fix to {len(vagner_it)} items...")
    for it in vagner_it:
        oid = it['offer_id']
        pid = it['product_id']
        
        # Get cat/type from info/status or info/list
        r_st = requests.post('https://api-seller.ozon.ru/v1/product/info/status', headers=H, json={'product_id': [pid]})
        st_data = r_st.json().get('result', {})
        cat_id = st_data.get('description_category_id')
        type_id = st_data.get('type_id')
        
        if not cat_id:
            r_at = requests.post('https://api-seller.ozon.ru/v3/product/info/list', headers=H, json={'product_id': [pid]})
            at_data = r_at.json().get('result', {}).get('items', [{}])[0]
            cat_id = at_data.get('description_category_id')
            type_id = at_data.get('type_id')

        print(f"  Updating {oid} (Cat:{cat_id}, Type:{type_id})...")
        new_model = "Жетон с гравировкой GRAVMIX"
        new_color = "Индивидуальный (v2)" if "17272" in oid else "Индивидуальный"
        
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
        print(f"  Result: {r_upd.status_code}")

if __name__ == "__main__":
    final_perfect_fix()
