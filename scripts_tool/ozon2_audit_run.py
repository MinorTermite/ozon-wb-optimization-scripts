import requests
import json
import time

H = {
    'Client-Id': '311191',
    'Api-Key': '88da03d6-8f00-4189-af6b-db145ec7689f',
    'Content-Type': 'application/json'
}

def audit():
    print("Fetching product list...")
    pids = []
    last_id = ""
    while True:
        body = {
            "filter": {"visibility": "ALL"},
            "last_id": last_id,
            "limit": 1000
        }
        r = requests.post("https://api-seller.ozon.ru/v3/product/list", headers=H, json=body, timeout=30)
        data = r.json()
        items = data.get("result", {}).get("items", [])
        if not items:
            break
        for it in items:
            pids.append(it['product_id'])
        last_id = data.get("result", {}).get("last_id", "")
        if not last_id:
            break

    print(f"Total products: {len(pids)}")
    if not pids:
        return

    # Fetch info with retry and smaller chunks
    print("Fetching product details...")
    products = []
    failed_pids = []
    
    # Process in chunks of 50 for stability
    for i in range(0, len(pids), 50):
        chunk = pids[i:i+50]
        success = False
        for attempt in range(3):
            try:
                r = requests.post("https://api-seller.ozon.ru/v3/product/info/list", headers=H, json={"product_id": chunk}, timeout=60)
                if r.status_code == 200:
                    products.extend(r.json().get("result", {}).get("items", []))
                    success = True
                    break
                else:
                    print(f"  Attempt {attempt+1} failed ({r.status_code}). Retrying...")
            except Exception as e:
                print(f"  Attempt {attempt+1} error: {e}. Retrying...")
            time.sleep(1)
        
        if not success:
            failed_pids.extend(chunk)
            print(f"  CRITICAL: Failed to fetch info for chunk at {i}")
        
        if i % 500 == 0:
            print(f"  Progress: {i}/{len(pids)}")
        time.sleep(0.1)

    # Dump for safety immediately
    with open('ozon2_products_dump.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

    # Fetch errors/status
    print("Fetching statuses...")
    errors = []
    for i in range(0, len(pids), 1000):
        chunk = pids[i:i+1000]
        r = requests.post("https://api-seller.ozon.ru/v1/product/info/status", headers=H, json={"product_id": chunk}, timeout=30)
        try:
            if r.status_code == 200:
                items = r.json().get('result', {}).get('items', [])
                for item in items:
                    state_failed = item.get('state', '') == 'failed'
                    if state_failed:
                        errors.append(item.get('state_failed', ''))
                    elif item.get('state_name', '') == 'Черновик' or item.get('state_name', '') == 'С ошибкой':
                        errors.append(item.get('state_description', 'Error'))
            else:
                print(f"Status API failed: {r.status_code}")
        except Exception as e:
            print(f"Status parse error: {e}")
        time.sleep(0.5)

    # Analyze only in-stock
    in_stock_products = []
    for p in products:
        # Check stock across all warehouses
        stock = p.get('stocks', {}).get('present', 0)
        if stock > 0:
            in_stock_products.append(p)

    total_all = len(products)
    total_active = len(in_stock_products)
    short_titles = 0
    no_rich = 0
    
    for p in in_stock_products:
        if len(p.get('name', '')) < 40: short_titles += 1
        # Check if description exists or if it contains rich content markers
        # In Ozon API v3 info/list, complex logic might be needed for rich, 
        # but let's check primary markers first.
        if not p.get('shipped_weight', 0): pass # just a placeholder for logic

    print("\n=== OZON CABINET 2 AUDIT (IN STOCK ONLY) ===")
    print(f"Total Products in Cabinet: {total_all}")
    print(f"Active Products (Stock > 0): {total_active}")
    print(f"Errors / Drafts in Active: {len([e for e in errors if 'in_active' in str(e)])} (Filtering logic pending status mapping)")
    print(f"Short Titles in Active (<40 chars): {short_titles}")
    
    # Save active list for next steps
    with open('ozon2_active_products.json', 'w', encoding='utf-8') as f:
        json.dump(in_stock_products, f, ensure_ascii=False, indent=2)

    print("\nNext step: Provide optimization plan for these", total_active, "items.")

if __name__ == "__main__":
    audit()
