import requests
import json
import time

H = {
    'Client-Id': '311191',
    'Api-Key': '88da03d6-8f00-4189-af6b-db145ec7689f',
    'Content-Type': 'application/json'
}

def analyze_heap_members():
    print("Fetching all items to identify heap members...")
    r_list = requests.post('https://api-seller.ozon.ru/v3/product/list', headers=H, json={'filter': {'visibility': 'IN_SALE'}, 'limit': 1000})
    pids = [it['product_id'] for it in r_list.json().get('result', {}).get('items', [])]
    
    print(f"Fetching attributes for {len(pids)} items...")
    all_attrs = []
    for i in range(0, len(pids), 50):
        batch = pids[i:i+50]
        r_at = requests.post('https://api-seller.ozon.ru/v4/product/info/attributes', headers=H, json={'filter': {'product_id': batch}, 'limit': 50})
        all_attrs.extend(r_at.json().get('result', []))

    # Targeted group: "Браслет с гравировкой GRAVMIX" (59 items)
    heap_items = []
    for res in all_attrs:
        attrs = res['attributes']
        m_name = next((a['values'][0]['value'] for a in attrs if a['id'] == 9048), None)
        if m_name == "Браслет с гравировкой GRAVMIX":
            heap_items.append(res)

    print(f"Analyzing {len(heap_items)} heap items...")
    
    final_analysis = []
    for item in heap_items:
        oid = item['offer_id']
        name = ""
        for a in item['attributes']:
            if a['id'] in [4180, 4191]:
                name = a['values'][0]['value'] if a['values'] else ""
                break
        
        final_analysis.append({
            'offer_id': oid,
            'name': name,
            'images': item.get('images', [])[:1], # Just first image for reference
            'attributes': item['attributes']
        })

    with open('ozon2_heap_final_audit.json', 'w', encoding='utf-8') as f:
        json.dump(final_analysis, f, ensure_ascii=False, indent=2)

    print("Saved heap analysis to ozon2_heap_final_audit.json")

if __name__ == "__main__":
    analyze_heap_members()
