import json
import os
import requests
from datetime import datetime

BASE_DIR = r'C:\Users\GravMix\.gemini\antigravity\playground\core-pulsar'
ANALYTICS_DIR = os.path.join(BASE_DIR, 'analytics')
ENV_PATH = os.path.join(BASE_DIR, '.env')

# Load API key
WB_KEY = ''
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('WB_API_KEY='):
                WB_KEY = line.strip().split('=', 1)[1]
                break

if not WB_KEY:
    print("Error: WB_API_KEY not found")
    exit(1)

headers = {
    'Authorization': WB_KEY,
    'Content-Type': 'application/json'
}

def fetch_all_feedbacks():
    print("Fetching feedbacks (up to 5000)...")
    url = 'https://feedbacks-api.wildberries.ru/api/v1/feedbacks'
    all_feedbacks = []
    
    # We take several pages if needed
    for skip in [0, 1000, 2000, 3000, 4000]:
        params = {
            'isAnswered': 'true',
            'take': 1000,
            'skip': skip,
            'order': 'dateDesc'
        }
        r = requests.get(url, headers=headers, params=params, timeout=30)
        if r.status_code == 200:
            fbs = r.json().get('data', {}).get('feedbacks', [])
            if not fbs: break
            all_feedbacks.extend(fbs)
            if len(fbs) < 1000: break
        else:
            print(f"Error at skip {skip}: {r.status_code}")
            break
            
    return all_feedbacks

def identify_refresh_candidates(feedbacks):
    stats = {}
    for f in feedbacks:
        det = f.get('productDetails', {})
        nm_id = det.get('nmId')
        if not nm_id: continue
        
        if nm_id not in stats:
            stats[nm_id] = {'count': 0, 'total_rating': 0, 'name': det.get('productName'), 'article': det.get('supplierArticle')}
            
        stats[nm_id]['count'] += 1
        stats[nm_id]['total_rating'] += f.get('productValuation', 5)
        
    candidates = []
    for nm_id, data in stats.items():
        avg_rating = data['total_rating'] / data['count']
        # Condition: less than 10 reviews AND rating < 3.5
        if data['count'] <= 10 and avg_rating < 3.5:
            candidates.append({
                'nmId': nm_id,
                'name': data['name'],
                'article': data['article'],
                'reviews_count': data['count'],
                'avg_rating': round(avg_rating, 2)
            })
            
    # Save candidates
    output_path = os.path.join(ANALYTICS_DIR, 'wb_refresh_candidates.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(candidates, f, ensure_ascii=False, indent=2)
        
    print(f"Found {len(candidates)} candidates for refresh.")
    return candidates

if __name__ == "__main__":
    fbs = fetch_all_feedbacks()
    if fbs:
        identify_refresh_candidates(fbs)
