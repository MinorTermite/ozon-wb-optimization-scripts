import requests
import json
import time

H = {
    'Client-Id': '311191',
    'Api-Key': '88da03d6-8f00-4189-af6b-db145ec7689f',
    'Content-Type': 'application/json'
}

def diagnose_heap():
    print("Fetching active products list...")
    r_list = requests.post('https://api-seller.ozon.ru/v3/product/list', headers=H, json={'filter': {'visibility': 'IN_SALE'}, 'limit': 1000})
    items = r_list.json().get('result', {}).get('items', [])
    pids = [it['product_id'] for it in items]
    
    # Get details for group members
    group_items = []
    heap_id = 4750151598
    for i in range(0, len(pids), 50):
        batch = pids[i:i+50]
        r_st = requests.post('https://api-seller.ozon.ru/v1/product/info/status', headers=H, json={'product_id': batch})
        if r_st.status_code == 200:
            try:
                res = r_st.json().get('result', {}).get('items', [])
                for it in res:
                    if it.get('model_id') == heap_id or it.get('group_id') == heap_id:
                        group_items.append(it)
            except Exception as e:
                print(f"Error parsing batch {i}: {e}. Text: {r_st.text[:200]}")
        else:
            print(f"Error status {r_st.status_code}: {r_st.text[:200]}")
        time.sleep(0.5)

    print(f"Found {len(group_items)} items in the heap group.")
    
    detailed_data = []
    for it in group_items:
        pid = it['product_id']
        oid = it['offer_id']
        name = it['name']
        
        # Get attributes and images (using v3 for stability if v4 fails)
        r_at = requests.post('https://api-seller.ozon.ru/v3/product/info/list', headers=H, json={'product_id': [pid], 'limit': 1})
        if r_at.status_code == 200:
            try:
                at_res = r_at.json().get('result', {}).get('items', [])
                if at_res:
                    it_info = at_res[0]
                    # Note: v3 info/list has different structure, but we need photo links etc.
                    # Let's try v4 again for one item to be safe
                    r4 = requests.post('https://api-seller.ozon.ru/v4/product/info/attributes', headers=H, json={'filter': {'product_id': [pid]}, 'limit': 1})
                    if r4.status_code == 200:
                        attrs_v4 = r4.json().get('result', [])
                        if attrs_v4:
                            it_info['attributes'] = attrs_v4[0].get('attributes', [])
                            it_info['images'] = attrs_v4[0].get('images', [])
                    
                    detailed_data.append(it_info)
            except Exception as e:
                print(f"Error parsing item {oid}: {e}")
        time.sleep(0.1)

    with open('ozon2_heap_deep_audit_v3.json', 'w', encoding='utf-8') as f:
        json.dump(detailed_data, f, ensure_ascii=False, indent=2)

    print(f"Audit saved to ozon2_heap_deep_audit_v3.json")

if __name__ == "__main__":
    diagnose_heap()
