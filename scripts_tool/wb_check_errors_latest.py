import requests, json

with open('.env', 'r', encoding='utf-8') as f:
    env = dict(line.strip().split('=', 1) for line in f if '=' in line and not line.startswith('#'))
H = {'Authorization': env['WB_API_KEY'], 'Content-Type': 'application/json'}

try:
    print("=== SERVER ERRORS ===")
    r = requests.post('https://content-api.wildberries.ru/content/v2/cards/error/list', headers=H, json={'locale':'ru'}, timeout=15)
    
    if r.status_code == 200:
        data = r.json()
        items = data.get('data', [])
        
        # Debug structure
        if isinstance(items, list):
            print("Items is expected list")
            pass
        elif isinstance(items, dict) and 'items' in items:
            items = items['items']
            
        unique_errors = set()
        err_count = 0
        for item in items:
            if isinstance(item, str):
                continue
                
            subjects = item.get('subjects', {})
            for subj_name, subj_data in subjects.items():
                for vc, err_list in subj_data.get('errors', {}).items():
                    err_count += 1
                    for err in err_list:
                        unique_errors.add(err)
                    if err_count <= 20:
                        print(f"[{vc}] -> {err_list}")
        
        print(f"Total cards with errors: {err_count}")
        print("\nUnique Error Types:")
        for e in unique_errors:
            print(f" - {e}")
    else:
        print(f"Error {r.status_code}: {r.text[:200]}")
except Exception as e:
    print(f"Exception: {e}")

try:
    print("\n=== FETCHING ALL CARDS ===")
    all_cards = []
    cursor = {"limit": 100}
    total = 0
    while True:
        body = {"settings": {"cursor": cursor, "filter": {"withPhoto": -1}}}
        r = requests.post('https://content-api.wildberries.ru/content/v2/get/cards/list', headers=H, json=body, timeout=30)
        
        if r.status_code != 200:
            print(f"Fetch list error: {r.status_code} {r.text[:200]}")
            break
            
        data = r.json().get('data', {})
        batch = data.get('cards', [])
        if not batch: break
        all_cards.extend(batch)
        total += len(batch)
        
        cur = data.get('cursor', {})
        if 'updatedAt' in cur:
            cursor['updatedAt'] = cur['updatedAt']
        if 'nmID' in cur:
            cursor['nmID'] = cur['nmID']
        
    with open('wb_cards_latest.json', 'w', encoding='utf-8') as f:
        json.dump(all_cards, f, ensure_ascii=False)
    
    print(f"Fetched {len(all_cards)} cards.")
    
    bad_dims = sum(1 for c in all_cards if not c.get('dimensions', {}).get('isValid', False) or c.get('dimensions', {}).get('length', 0) == 0)
    print(f"Cards missing valid dimensions: {bad_dims}")

except Exception as e:
    print(f"Exception: {e}")
