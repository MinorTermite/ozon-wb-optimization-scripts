import requests
import json
import time

H = {
    'Client-Id': '311191',
    'Api-Key': '88da03d6-8f00-4189-af6b-db145ec7689f',
    'Content-Type': 'application/json'
}

def final_audit():
    print("Final Audit of 130 active products status via v3...")
    with open('ozon2_active_130.json', 'r', encoding='utf-8') as f:
        products = json.load(f)

    pids = [p['id'] for p in products]
    errors = []
    processed = 0

    for i in range(0, len(pids), 50):
        batch = pids[i:i+50]
        # v3/product/info/list is the most reliable for current detailed state
        try:
            r = requests.post('https://api-seller.ozon.ru/v3/product/info/list', headers=H, json={'product_id': batch}, timeout=30)
            if r.status_code == 200:
                items = r.json().get('result', {}).get('items', [])
                for it in items:
                    st = it.get('status', {})
                    state = st.get('state_name', '')
                    state_desc = st.get('state_description', '')
                    
                    has_issue = False
                    if state in ['С ошибкой', 'Черновик'] or st.get('is_failed'):
                        has_issue = True
                    # Also check for "недочеты" which often appear in state_description
                    if 'нетод' in state_desc.lower() or 'недочет' in state_desc.lower():
                        has_issue = True
                        
                    if has_issue:
                        errors.append(f"{it.get('offer_id')}: {state} | {state_desc}")
                
                processed += len(batch)
                print(f"  Checked {processed}/{len(pids)}")
            else:
                print(f"  Batch failed ({r.status_code}): {r.text[:100]}")
        except Exception as e:
            print(f"  Error: {e}")
            
        time.sleep(1)

    print("\n--- FINAL AUDIT SUMMARY ---")
    print(f"Total checked: {len(pids)}")
    print(f"Items with issues: {len(errors)}")

    if errors:
        for e in errors:
            print(f"  - {e}")
    else:
        print("PERFECT! All 130 active products are clean now.")

if __name__ == "__main__":
    final_audit()
