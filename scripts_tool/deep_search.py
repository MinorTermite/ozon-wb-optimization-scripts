import json
import os

def search_everywhere():
    target = 'кни'
    results = []
    
    # 1. WB Cards
    if os.path.exists('wb_cards_seo_dump.json'):
        with open('wb_cards_seo_dump.json', 'r', encoding='utf-8') as f:
            cards = json.load(f)
            for c in cards:
                if target in str(c).lower():
                    results.append({'file': 'wb_cards_seo_dump.json', 'nmID': c.get('nmID'), 'title': c.get('title')})
                    
    # 2. Ozon Cards
    ozon_path = os.path.join('data_dump', 'ozon2_active_attributes.json')
    if os.path.exists(ozon_path):
        with open(ozon_path, 'r', encoding='utf-8') as f:
            ozon = json.load(f)
            for item in ozon:
                if target in str(item).lower():
                    results.append({'file': 'ozon2_active_attributes.json', 'offer_id': item.get('offer_id'), 'name': item.get('name')})

    # 3. All files in data_dump and analytics
    for d in ['data_dump', 'analytics']:
        if not os.path.exists(d): continue
        for f_name in os.listdir(d):
            if f_name.endswith('.json'):
                path = os.path.join(d, f_name)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if target in content.lower():
                            results.append({'file': path, 'status': 'found match in text'})
                except: pass

    with open('search_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    search_everywhere()
