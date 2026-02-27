import json
import os

BASE_DIR = r'C:\Users\GravMix\.gemini\antigravity\playground\core-pulsar'
REVIEWS_PATH = os.path.join(BASE_DIR, 'analytics', 'wb_negative_reviews.json')
DATA_DUMP_PATH = os.path.join(BASE_DIR, 'data_dump', 'wb_cards_seo_dump.json')

def get_recreation_candidates():
    if not os.path.exists(REVIEWS_PATH):
        print("Reviews file not found")
        return []
    
    with open(REVIEWS_PATH, 'r', encoding='utf-8') as f:
        reviews = json.load(f)
    
    # Process reviews to group by nmID
    nm_stats = {}
    for rev in reviews:
        nm_id = rev.get('nmId')
        if not nm_id: continue
        
        if nm_id not in nm_stats:
            nm_stats[nm_id] = {'count': 0, 'total_rating': 0}
        
        nm_stats[nm_id]['count'] += 1
        nm_stats[nm_id]['total_rating'] += rev.get('productValuation', 0)
    
    candidates = []
    for nm_id, stats in nm_stats.items():
        avg = stats['total_rating'] / stats['count']
        # If any significant negative feedback exists, we consider it
        if avg < 4.0:
            candidates.append(nm_id)
            
    print(f"Found {len(candidates)} candidates for recreation based on ratings.")
    return candidates

if __name__ == "__main__":
    candidates = get_recreation_candidates()
    # Save candidates for next step
    with open(os.path.join(BASE_DIR, 'analytics', 'wb_recreate_nmids.json'), 'w', encoding='utf-8') as f:
        json.dump(candidates, f)
