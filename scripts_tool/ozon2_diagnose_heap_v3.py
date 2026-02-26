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
    
    # Use v3/product/info/list to get info including model_id
    heap_id = 4750151598
    group_items = []
    
    print(f"Fetching details for {len(pids)} products...")
    for i in range(0, len(pids), 50):
        batch = pids[i:i+50]
        r_info = requests.post('https://api-seller.ozon.ru/v3/product/info/list', headers=H, json={'product_id': batch})
        if r_info.status_code == 200:
            res = r_info.json().get('result', {}).get('items', [])
            for it in res:
                # Ozon v3 info list returns model_id as the grouping ID
                if it.get('model_id') == heap_id:
                    group_items.append(it)
        else:
            print(f"Error v3 info list: {r_info.status_code}")
        time.sleep(0.5)

    print(f"Found {len(group_items)} items explicitly in heap group {heap_id}.")
    
    # Also fetch attributes for items to see current Model Names
    # because even if model_id is same, Model Name attribute 9048 should have changed
    # if I applied it. If they are still in one group, either 9048 didn't change 
    # or Ozon is overriding it.
    
    detailed_data = []
    for it in group_items:
        pid = it['product_id']
        oid = it['offer_id']
        name = it['name']
        
        # Get attributes v4
        r4 = requests.post('https://api-seller.ozon.ru/v4/product/info/attributes', headers=H, json={'filter': {'product_id': [pid]}, 'limit': 1})
        at_v4 = {}
        if r4.status_code == 200:
            at_res = r4.json().get('result', [])
            if at_res:
                at_v4 = at_res[0]

        detailed_data.append({
            'product_id': pid,
            'offer_id': oid,
            'name': name,
            'model_id': it.get('model_id'),
            'price': it.get('price'),
            'images': at_v4.get('images', []),
            'attributes': at_v4.get('attributes', [])
        })
        time.sleep(0.1)

    with open('ozon2_heap_deep_audit_v4.json', 'w', encoding='utf-8') as f:
        json.dump(detailed_data, f, ensure_ascii=False, indent=2)

    print(f"Detailed audit saved to ozon2_heap_deep_audit_v4.json")

if __name__ == "__main__":
    diagnose_heap()
