import json
import os
from collections import defaultdict

def generate_report():
    print("Marketplace | ID/NM | Name | Total Stock")
    print("-" * 80)
    
    # 1. WB
    stock_map = defaultdict(int)
    stocks_path = os.path.join('analytics', 'wb_stocks.json')
    if os.path.exists(stocks_path):
        with open(stocks_path, 'r', encoding='utf-8') as f:
            for s in json.load(f):
                stock_map[s.get('nmId')] += s.get('quantity', 0)
                
    if os.path.exists('wb_cards_seo_dump.json'):
        with open('wb_cards_seo_dump.json', 'r', encoding='utf-8') as f:
            for c in json.load(f):
                nmID = c['nmID']
                title = c.get('title', 'NO TITLE')
                print(f"WB | {nmID} | {title} | {stock_map.get(nmID, 0)}")

    # 2. Ozon
    ozon_path = os.path.join('data_dump', 'ozon2_active_attributes.json')
    if os.path.exists(ozon_path):
        with open(ozon_path, 'r', encoding='utf-8') as f:
            for item in json.load(f):
                oid = item.get('offer_id')
                name = item.get('name', 'NO NAME')
                print(f"Ozon | {oid} | {name} | (Stock unknown - Ozon)")

if __name__ == "__main__":
    generate_report()
