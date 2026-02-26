import json
import requests
import time

with open('.env', 'r', encoding='utf-8') as f:
    env = dict(line.strip().split('=', 1) for line in f if '=' in line and not line.startswith('#'))

H = {'Authorization': env['WB_API_KEY'], 'Content-Type': 'application/json'}

def split_and_merge():
    with open('wb_cards_seo_dump.json', 'r', encoding='utf-8') as f:
        cards = json.load(f)

    zodiac_keywords = ['овен', 'телец', 'близнец', 'рак', 'лев', 'дев', 'весы', 'скорпион', 'стрелец', 'козерог', 'водолей', 'рыб']
    
    nm_list = []
    
    for c in cards:
        t = c.get('title', '').lower()
        nm = c.get('nmID')
        imt = c.get('imtID')
        
        if 'браслет' in t and any(kw in t for kw in zodiac_keywords):
            nm_list.append({'nmID': nm, 'imtID': imt})

    # Group by IMT
    imts = {}
    for item in nm_list:
        imts.setdefault(item['imtID'], []).append(item['nmID'])

    print(f"Total Zodiac items: {len(nm_list)}")
    # We will pick two distinct IMTs and split the nmIDs between them
    target_1 = list(imts.keys())[0]
    target_2 = list(imts.keys())[1]

    all_nms_to_move = []
    for imt, nms in imts.items():
        if imt not in [target_1, target_2]:
            all_nms_to_move.extend(nms)
            
    # Split all_nms_to_move into two chunks so that target_1 and target_2 don't exceed 30
    # Currently target_1 has len(imts[target_1]) items, etc.
    chunk_1 = []
    chunk_2 = []
    
    cap_1 = 30 - len(imts[target_1])
    cap_2 = 30 - len(imts[target_2])
    
    for nm in all_nms_to_move:
        if len(chunk_1) < cap_1:
            chunk_1.append(nm)
        else:
            chunk_2.append(nm)
            
    print(f"Moving {len(chunk_1)} to {target_1}")
    if chunk_1:
        r1 = requests.post("https://content-api.wildberries.ru/content/v2/cards/moveNm", headers=H, json={"targetIMT": int(target_1), "nmIDs": [int(n) for n in chunk_1]})
        print(r1.status_code, r1.text)
        
    print(f"Moving {len(chunk_2)} to {target_2}")
    if chunk_2:
        r2 = requests.post("https://content-api.wildberries.ru/content/v2/cards/moveNm", headers=H, json={"targetIMT": int(target_2), "nmIDs": [int(n) for n in chunk_2]})
        print(r2.status_code, r2.text)

if __name__ == "__main__":
    split_and_merge()
