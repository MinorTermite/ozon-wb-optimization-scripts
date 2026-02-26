import json
import requests
import time

with open('.env', 'r', encoding='utf-8') as f:
    env = dict(line.strip().split('=', 1) for line in f if '=' in line and not line.startswith('#'))

H = {'Authorization': env['WB_API_KEY'], 'Content-Type': 'application/json'}

def execute_merge():
    with open('wb_cards_seo_dump.json', 'r', encoding='utf-8') as f:
        cards = json.load(f)

    # Re-build the clusters exactly as in the plan
    clusters = {
        "Браслеты: Знаки Зодиака": {'keywords': ['овен', 'телец', 'близнец', 'рак', 'лев', 'дев', 'весы', 'скорпион', 'стрелец', 'козерог', 'водолей', 'рыб'], 'require': 'браслет', 'items': []},
        "Браслеты: Семья (Мужчинам)": {'keywords': ['пап', 'муж', 'сын', 'дед', 'брат'], 'require': 'браслет', 'items': []},
        "Браслеты: Семья (Женщинам)": {'keywords': ['мам', 'жен', 'доч', 'бабуш', 'сестр'], 'require': 'браслет', 'items': []},
        "Брелоки: Семья (Мужчинам)": {'keywords': ['пап', 'муж', 'сын', 'дед', 'брат'], 'require': 'брелок', 'items': []},
        "Брелоки: Семья (Женщинам)": {'keywords': ['мам', 'жен', 'доч', 'бабуш', 'сестр'], 'require': 'брелок', 'items': []},
        "Брелоки: Автомобильные": {'keywords': ['авто', 'машин', 'рул', 'газ'], 'require': 'брелок', 'items': []}
    }

    # Populate clusters
    for c in cards:
        t = c.get('title', '').lower()
        nm = c.get('nmID')
        imt = c.get('imtID')
        vc = c.get('vendorCode')
        
        for cname, cdata in clusters.items():
            if cdata['require'] in t or not cdata['require']:
                if any(kw in t for kw in cdata['keywords']):
                    cdata['items'].append({'nmID': nm, 'imtID': imt, 'vc': vc, 'title': c.get('title')})
                    break 

    print("=== STARTING MERGE (moveNm) ===\n")
    url = "https://content-api.wildberries.ru/content/v2/cards/moveNm"

    for cname, cdata in clusters.items():
        if len(cdata['items']) > 1:
            imts = set(i['imtID'] for i in cdata['items'])
            if len(imts) > 1:
                target_imt = cdata['items'][0]['imtID']
                nm_to_move = [i['nmID'] for i in cdata['items'][1:] if i['imtID'] != target_imt]
                
                print(f"Cluster: {cname}")
                print(f"  -> Moving {len(nm_to_move)} NMs into Target imtID: {target_imt}")
                
                # WB API requires body: { "targetIMT": int, "nmIDs": [int] }
                body = {
                    "targetIMT": int(target_imt),
                    "nmIDs": [int(n) for n in nm_to_move]
                }
                
                # We should avoid moving too many at once if there's a limit, but usually arrays are fine.
                # The documentation states nmIDs is an array of Integers.
                
                r = requests.post(url, headers=H, json=body)
                print(f"  -> Status: {r.status_code}")
                if r.status_code != 200:
                    print(f"  -> Error: {r.text}")
                else:
                    data = r.json()
                    if data.get('error'):
                        print(f"  -> WB Error: {data.get('errorText')} - {data.get('additionalErrors')}")
                    else:
                        print(f"  -> SUCCESS! Merged {len(nm_to_move)} cards into {target_imt}")
                        
                time.sleep(2) # rate limit safety
            else:
                print(f"Cluster: {cname} is already fully merged (imtID: {list(imts)[0]})")

if __name__ == "__main__":
    execute_merge()
