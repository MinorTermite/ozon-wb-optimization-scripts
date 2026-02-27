import json
import os

def search():
    keywords = ['книж', 'книга', 'book']
    matches = []
    
    # Check fresh dump
    dump_path = 'wb_cards_seo_dump.json'
    if os.path.exists(dump_path):
        with open(dump_path, 'r', encoding='utf-8') as f:
            cards = json.load(f)
            for c in cards:
                text = str(c).lower()
                if any(k in text for k in keywords):
                    matches.append({
                        'source': 'wb_cards_seo_dump.json',
                        'nmID': c.get('nmID'),
                        'title': c.get('title'),
                        'description': c.get('description', '')[:50] + '...'
                    })

    # Check ozon data
    ozon_path = os.path.join('data_dump', 'ozon2_active_attributes.json')
    if os.path.exists(ozon_path):
        with open(ozon_path, 'r', encoding='utf-8') as f:
            ozon = json.load(f)
            for item in ozon:
                text = str(item).lower()
                if any(k in text for k in keywords):
                    matches.append({
                        'source': 'ozon2_active_attributes.json',
                        'offer_id': item.get('offer_id'),
                        'name': item.get('name')
                    })

    print(json.dumps(matches, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    search()
