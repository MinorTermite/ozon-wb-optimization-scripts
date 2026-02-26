import requests
import json
import time
from collections import defaultdict

H = {
    'Client-Id': '311191',
    'Api-Key': '88da03d6-8f00-4189-af6b-db145ec7689f',
    'Content-Type': 'application/json'
}

def split_ozon_heap():
    print("Step 1: Identifying products in the large group...")
    # Fetch list to get PIDs
    r_list = requests.post('https://api-seller.ozon.ru/v3/product/list', headers=H, json={'filter': {'visibility': 'IN_SALE'}, 'limit': 1000})
    pids = [it['product_id'] for it in r_list.json().get('result', {}).get('items', [])]
    
    # Fetch attributes
    all_attrs = []
    for i in range(0, len(pids), 50):
        batch = pids[i:i+50]
        r_at = requests.post('https://api-seller.ozon.ru/v4/product/info/attributes', headers=H, json={'filter': {'product_id': batch}, 'limit': 50})
        all_attrs.extend(r_at.json().get('result', []))

    # Identify the target heap group items
    target_oids = []
    # Based on previous run, group '   GRAVMIX' (69 items)
    # The user screenshot confirms it's a mix of zodiacs, gifts, etc.
    
    # We will also categorize items from SMALLER groups if they fit the sense.
    
    updates = []
    for item in all_attrs:
        attrs = item['attributes']
        oid = item['offer_id']
        cat_id = item['description_category_id']
        type_id = item['type_id']
        
        # Get Title
        name = ""
        for a in attrs:
            if a['id'] in [4180, 4191]:
                name = a['values'][0]['value'] if a['values'] else ""
                break
        
        if not name: continue
        n_low = name.lower()
        
        # Determine logical group name
        new_model = "Браслеты GRAVMIX" # Default fallback
        
        if "знак" in n_low or "зодиак" in n_low:
            new_model = "Браслет со знаком зодиака GRAVMIX"
        elif "сыну" in n_low or "дочери" in n_low or "ребенку" in n_low or "сыночек" in n_low:
            new_model = "Браслет подарок детям GRAVMIX"
        elif "папе" in n_low or "маме" in n_low or "родител" in n_low:
            new_model = "Браслет подарок родителям GRAVMIX"
        elif "парн" in n_low or "любим" in n_low or "двоих" in n_low or "сердц" in n_low:
            new_model = "Браслет для влюбленных GRAVMIX"
        elif "молитв" in n_low or "отче наш" in n_low or "спаси и сохрани" in n_low:
            new_model = "Браслет с молитвой GRAVMIX"
        else:
            new_model = "Браслет с гравировкой GRAVMIX"

        # Check if Model Name 9048 already matches
        current_model = next((a['values'][0]['value'] for a in attrs if a['id'] == 9048), None)
        
        if current_model != new_model:
            updates.append({
                "offer_id": oid,
                "description_category_id": cat_id,
                "type_id": type_id,
                "attributes": [{"id": 9048, "values": [{"value": new_model}]}]
            })

    print(f"Prepared {len(updates)} grouping updates.")
    
    # Execute in batches
    BATCH_SIZE = 10
    ok, err = 0, 0
    for i in range(0, len(updates), BATCH_SIZE):
        batch = updates[i:i+BATCH_SIZE]
        r = requests.post('https://api-seller.ozon.ru/v1/product/attributes/update', headers=H, json={"items": batch})
        if r.status_code == 200:
            ok += len(batch)
            print(f"  Batch {i//BATCH_SIZE + 1} Success. ({ok}/{len(updates)})")
        else:
            err += len(batch)
            print(f"  Batch {i//BATCH_SIZE + 1} Error: {r.status_code} {r.text[:200]}")
        time.sleep(1)

    print(f"\nOZON SPLIT FINISHED: {ok} OK, {err} ERR")

if __name__ == "__main__":
    split_ozon_heap()
