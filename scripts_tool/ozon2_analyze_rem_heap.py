import requests
import json
import time

H = {
    'Client-Id': '311191',
    'Api-Key': '88da03d6-8f00-4189-af6b-db145ec7689f',
    'Content-Type': 'application/json'
}

def analyze_remaining_heap():
    print("Fetching active products and attributes...")
    r_list = requests.post('https://api-seller.ozon.ru/v3/product/list', headers=H, json={'filter': {'visibility': 'IN_SALE'}, 'limit': 1000})
    pids = [it['product_id'] for it in r_list.json().get('result', {}).get('items', [])]
    
    all_attrs = []
    for i in range(0, len(pids), 50):
        batch = pids[i:i+50]
        r_at = requests.post('https://api-seller.ozon.ru/v4/product/info/attributes', headers=H, json={'filter': {'product_id': batch}, 'limit': 50})
        res = r_at.json().get('result', [])
        if res:
            all_attrs.extend(res)
        time.sleep(0.5)

    heap_oids = []
    for res in all_attrs:
        m_name = next((a['values'][0]['value'] for a in res['attributes'] if a['id'] == 9048), 'N')
        if m_name == 'Браслеты с гравировкой GRAVMIX':
            heap_oids.append(res['offer_id'])

    print(f"Items in remaining heap: {len(heap_oids)}")
    
    final_details = []
    for oid in heap_oids[:100]: # Safety limit
        r_info = requests.post('https://api-seller.ozon.ru/v2/product/info/list', headers=H, json={'offer_id': [oid]})
        if r_info.status_code == 200:
            try:
                it = r_info.json().get('result', {}).get('items', [])[0]
                final_details.append({
                    'offer_id': it.get('offer_id'),
                    'name': it.get('name')
                })
                print(f" - {it.get('offer_id')}: {it.get('name')[:80]}")
            except:
                pass
        time.sleep(0.1)

    with open('ozon2_remaining_heap.json', 'w', encoding='utf-8') as f:
        json.dump(final_details, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    analyze_remaining_heap()
