import requests
import json
import time
from collections import defaultdict

H = {
    'Client-Id': '311191',
    'Api-Key': '88da03d6-8f00-4189-af6b-db145ec7689f',
    'Content-Type': 'application/json'
}

def total_reverification():
    print("Step 1: Fetching all active products (IN_SALE)...")
    r_list = requests.post('https://api-seller.ozon.ru/v3/product/list', headers=H, json={'filter': {'visibility': 'IN_SALE'}, 'limit': 1000}, timeout=30)
    if r_list.status_code != 200:
        print(f"Failed to fetch list: {r_list.text}")
        return
    
    items = r_list.json().get('result', {}).get('items', [])
    pids = [it['product_id'] for it in items]
    print(f"Found {len(pids)} active products.")

    print("\nStep 2: Fetching detailed info and statuses...")
    all_data = []
    for i in range(0, len(pids), 50):
        batch = pids[i:i+50]
        r = requests.post('https://api-seller.ozon.ru/v3/product/info/list', headers=H, json={'product_id': batch}, timeout=60)
        if r.status_code == 200:
            all_data.extend(r.json().get('result', {}).get('items', []))
        else:
            print(f"  Batch failed: {r.status_code}")
        time.sleep(0.5)

    print("\nStep 3: Checking for errors and warnings (is_failed, state_description)...")
    issues = []
    for it in all_data:
        st = it.get('status', {})
        state = st.get('state_name', '')
        state_desc = st.get('state_description', '')
        oid = it.get('offer_id')
        
        if st.get('is_failed') or state in ['С ошибкой', 'Черновик'] or 'недочет' in state_desc.lower():
            issues.append(f"{oid}: {state} | {state_desc}")

    if issues:
        print(f"Found {len(issues)} items with potential issues:")
        for iss in issues:
            print(f"  - {iss}")
    else:
        print("No critical status errors found.")

    print("\nStep 4: Checking for duplicate variants in Model Groups...")
    # Group by Model Name (Attr 9048)
    # We need attributes for this
    print("Fetching attributes for all products...")
    all_attrs = []
    for i in range(0, len(pids), 50):
        batch = pids[i:i+50]
        r = requests.post('https://api-seller.ozon.ru/v4/product/info/attributes', headers=H, json={'filter': {'product_id': batch}, 'limit': 50}, timeout=60)
        if r.status_code == 200:
            all_attrs.extend(r.json().get('result', []))
        time.sleep(1)

    models = defaultdict(lambda: defaultdict(list))
    for it in all_attrs:
        oid = it.get('offer_id')
        m_name = ""
        c_id = 0
        c_name = ""
        size = ""
        
        for a in it.get('attributes', []):
            aid = a.get('id')
            if aid == 9048: m_name = a.get('values')[0].get('value') if a.get('values') else ""
            if aid == 10096: c_id = a.get('values')[0].get('dictionary_value_id') if a.get('values') else 0
            if aid == 10097: c_name = a.get('values')[0].get('value') if a.get('values') else ""
            if aid == 5326: size = a.get('values')[0].get('value') if a.get('values') else ""

        if m_name:
            # A variant is uniquely identified by color and size in Ozon
            variant_key = (c_id, c_name, size)
            models[m_name][variant_key].append(oid)

    collisions = []
    for m, variants in models.items():
        for vkey, skus in variants.items():
            if len(skus) > 1:
                collisions.append({
                    'model': m,
                    'variant': vkey,
                    'skus': skus
                })

    if collisions:
        print(f"\nFOUND {len(collisions)} GROUPING COLLISIONS (duplicate variants in one model):")
        for col in collisions:
            print(f"  Model: {col['model']}")
            print(f"    Variant: ColorID={col['variant'][0]}, ColorName='{col['variant'][1]}', Size='{col['variant'][2]}'")
            print(f"    SKUs: {col['skus']}")
    else:
        print("\nVerification successful: No grouping collisions found.")

if __name__ == "__main__":
    total_reverification()
