import json
import collections

with open('.env', 'r', encoding='utf-8') as f:
    env = dict(line.strip().split('=', 1) for line in f if '=' in line and not line.startswith('#'))

H = {'Authorization': env['WB_API_KEY'], 'Content-Type': 'application/json'}

def get_groups():
    with open('wb_cards_seo_dump.json', 'r', encoding='utf-8') as f:
        cards = json.load(f)

    # We will strictly cluster by exact keywords
    clusters = {
        "Браслеты: Знаки Зодиака": {'keywords': ['овен', 'телец', 'близнец', 'рак', 'лев', 'дев', 'весы', 'скорпион', 'стрелец', 'козерог', 'водолей', 'рыб'], 'require': 'браслет', 'items': []},
        
        "Браслеты: Семья (Мужчинам)": {'keywords': ['пап', 'муж', 'сын', 'дед', 'брат'], 'require': 'браслет', 'items': []},
        "Браслеты: Семья (Женщинам)": {'keywords': ['мам', 'жен', 'доч', 'бабуш', 'сестр'], 'require': 'браслет', 'items': []},
        
        "Брелоки: Семья (Мужчинам)": {'keywords': ['пап', 'муж', 'сын', 'дед', 'брат'], 'require': 'брелок', 'items': []},
        "Брелоки: Семья (Женщинам)": {'keywords': ['мам', 'жен', 'доч', 'бабуш', 'сестр'], 'require': 'брелок', 'items': []},
        
        "Брелоки: Автомобильные": {'keywords': ['авто', 'машин', 'рул', 'газ'], 'require': 'брелок', 'items': []},
        "Парные украшения": {'keywords': ['парн', 'половинк', 'влюбл'], 'require': '', 'items': []},
    }

    # Tracking what is already clustered to avoid overlaps
    clustered_nms = set()

    for c in cards:
        t = c.get('title', '').lower()
        nm = c.get('nmID')
        imt = c.get('imtID')
        vc = c.get('vendorCode')
        
        for cname, cdata in clusters.items():
            if cdata['require'] in t or not cdata['require']:
                if any(kw in t for kw in cdata['keywords']):
                    cdata['items'].append({'nmID': nm, 'imtID': imt, 'vc': vc, 'title': c.get('title')})
                    clustered_nms.add(nm)
                    break 

    print("=== ИТОГОВЫЕ ГРУППЫ ДЛЯ СКЛЕЙКИ ===")
    for cname, cdata in clusters.items():
        if len(cdata['items']) > 1:
            # Check if they are already merged (same imtID)
            imts = set(i['imtID'] for i in cdata['items'])
            if len(imts) > 1:
                print(f"\n[ГОТОВО К СКЛЕЙКЕ] {cname} (Товаров: {len(cdata['items'])}, Разных карточек: {len(imts)})")
                target_imt = cdata['items'][0]['imtID']
                nm_to_move = [i['nmID'] for i in cdata['items'][1:] if i['imtID'] != target_imt]
                
                print(f"  -> Target imtID: {target_imt}")
                print(f"  -> NM IDs to move: {nm_to_move}")
                for i in cdata['items']:
                    print(f"     * {i['title']} [{i['vc']}] (imt: {i['imtID']})")
            else:
                print(f"\n[УЖЕ СКЛЕЕНО] {cname} (Товаров: {len(cdata['items'])}, все в imtID {list(imts)[0]})")

if __name__ == "__main__":
    get_groups()
