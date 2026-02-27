import json
import os
from collections import defaultdict

def audit():
    # 1. WB DATA
    # Load cards
    cards_path = 'wb_cards_seo_dump.json'
    cards = []
    if os.path.exists(cards_path):
        with open(cards_path, 'r', encoding='utf-8') as f:
            cards = json.load(f)
            
    # Load stocks
    stocks_path = os.path.join('analytics', 'wb_stocks.json')
    stock_map = defaultdict(int)
    if os.path.exists(stocks_path):
        with open(stocks_path, 'r', encoding='utf-8') as f:
            stocks = json.load(f)
            for s in stocks:
                nm_id = s.get('nmId')
                if nm_id:
                    stock_map[nm_id] += s.get('quantity', 0)

    print("\n--- WILDBERRIES PRODUCTS & STOCKS ---")
    matched_book = []
    for c in cards:
        nm_id = c['nmID']
        title = c.get('title', 'NO TITLE')
        qty = stock_map.get(nm_id, 0)
        
        # Look for "book" or similar manually
        search_blob = (str(title) + ' ' + str(c.get('description', ''))).lower()
        if any(k in search_blob for k in ['книга', 'книж', 'book', 'медальон', 'кулон']):
            matched_book.append(f"NM {nm_id}: {title} | Stock: {qty}")
            # print(f"NM {nm_id}: {title} | Stock: {qty}")

    # 2. OZON DATA
    ozon_path = os.path.join('data_dump', 'ozon2_active_attributes.json')
    print("\n--- OZON PRODUCTS ---")
    if os.path.exists(ozon_path):
        with open(ozon_path, 'r', encoding='utf-8') as f:
            ozon = json.load(f)
            for item in ozon:
                name = item.get('name', 'NO NAME')
                oid = item.get('offer_id')
                if any(k in name.lower() for k in ['книга', 'книж', 'book', 'медальон', 'кулон']):
                    print(f"OFFER {oid}: {name}")

    if matched_book:
        print("\nMatched WB Items (possible 'book pendant'):")
        for mb in matched_book:
            print(mb)
    else:
        print("\nNo 'book' or 'pendant' / 'medallion' keywords found in WB titles.")

if __name__ == "__main__":
    audit()
