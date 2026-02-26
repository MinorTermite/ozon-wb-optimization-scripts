import requests
import json
import time

H = {
    'Client-Id': '311191',
    'Api-Key': '88da03d6-8f00-4189-af6b-db145ec7689f',
    'Content-Type': 'application/json'
}

def diagnose_heap():
    print("Fetching items in group 4750151598...")
    # Fetch active products
    r_list = requests.post('https://api-seller.ozon.ru/v3/product/list', headers=H, json={'filter': {'visibility': 'IN_SALE'}, 'limit': 1000})
    items = r_list.json().get('result', {}).get('items', [])
    pids = [it['product_id'] for it in items]
    
    # Get status for all to identify group members
    group_items = []
    for i in range(0, len(pids), 100):
        batch = pids[i:i+100]
        r_st = requests.post('https://api-seller.ozon.ru/v1/product/info/status', headers=H, json={'product_id': batch})
        res = r_st.json().get('result', {}).get('items', [])
        for it in res:
            if it.get('model_id') == 4750151598 or it.get('group_id') == 4750151598:
                group_items.append(it)

    print(f"Found {len(group_items)} items in the heap group.")
    
    detailed_data = []
    for it in group_items:
        pid = it['product_id']
        oid = it['offer_id']
        name = it['name']
        
        # Get attributes and images
        r_at = requests.post('https://api-seller.ozon.ru/v4/product/info/attributes', headers=H, json={'filter': {'product_id': [pid]}, 'limit': 1})
        at_res = r_at.json().get('result', [])
        
        item_data = {
            'product_id': pid,
            'offer_id': oid,
            'name': name,
            'group_id': it.get('group_id'),
            'model_id': it.get('model_id'),
            'attributes': []
        }
        
        if at_res:
            item_data['attributes'] = at_res[0].get('attributes', [])
            item_data['images'] = at_res[0].get('images', [])
            
        detailed_data.append(item_data)
        time.sleep(0.1)

    with open('ozon2_heap_deep_audit.json', 'w', encoding='utf-8') as f:
        json.dump(detailed_data, f, ensure_ascii=False, indent=2)

    print(f"Audit saved to ozon2_heap_deep_audit.json. Analyzing...")
    
    # Summary of unique Model Names currently set
    model_names = {}
    for item in detailed_data:
        m_name = "NOT SET"
        for a in item['attributes']:
            if a['id'] == 9048:
                m_name = a['values'][0]['value'] if a['values'] else "EMPTY"
                break
        model_names[m_name] = model_names.get(m_name, 0) + 1
        
    print("\nCurrent Model Names in this group:")
    for name, count in model_names.items():
        print(f" - '{name}': {count} items")

if __name__ == "__main__":
    diagnose_heap()
