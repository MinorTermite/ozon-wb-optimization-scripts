import requests
import json
import time
import re

H = {
    'Client-Id': '311191',
    'Api-Key': '88da03d6-8f00-4189-af6b-db145ec7689f',
    'Content-Type': 'application/json'
}

BASE_TAGS = ["гравировка", "подарок", "сувенир", "аксессуар", "эксклюзив", "ручная работа"]

def generate_hashtags(name):
    tags = list(BASE_TAGS)
    n = name.lower()
    
    if "сын" in n or "любимому" in n or "муж" in n:
        tags.extend(["подарок мужу", "подарок сыну", "для него", "мужской аксессуар"])
    if "доч" in n or "маме" in n or "жен" in n:
        tags.extend(["подарок маме", "подарок дочери", "для нее", "женский аксессуар"])
    if "брелок" in n:
        tags.extend(["брелок для ключей", "брелок на заказ", "автоаксессуар"])
    if "жетон" in n or "медальон" in n:
        tags.extend(["жетон с гравировкой", "медальон", "подвеска"])
    if "браслет" in n:
        tags.extend(["браслет с надписью", "кожаный браслет", "стильный браслет"])
        
    # Zodiac signs
    zodiacs = ["овен", "телец", "близнецы", "рак", "лев", "дева", "весы", "скорпион", "стрелец", "козерог", "водолей", "рыбы"]
    for z in zodiacs:
        if z in n:
            tags.append(f"знак зодиака {z.capitalize()}")
            tags.append("астрология")
            break
            
    # Deduplicate and format
    seen = set()
    unique = []
    for t in tags:
        if t.lower() not in seen:
            seen.add(t.lower())
            unique.append("#" + t.replace(" ", "_"))
    return " ".join(unique[:30])

def expand_title(name):
    if len(name) >= 50:
        return name
    
    n = name.strip()
    # Basic logic to expand "Брелок для ключей" etc.
    if "Брелок для ключей" in n:
        n = "Брелок для ключей автомобиля металлический с лазерной гравировкой, подарок"
    if "Медальон" in n or "Жетон" in n:
        n += " из ювелирной стали с эксклюзивной гравировкой"
    if "Браслет" in n:
        n += " кожаный мужской с надписью и гравировкой"
        
    # Append keywords if still short
    if len(n) < 60:
        n += ", оригинальный подарок близкому человеку"
        
    return n[:120]

def apply_seo():
    print("Loading data...")
    # The script is run from project root, data is in data_dump
    with open('data_dump/ozon2_active_attributes.json', 'r', encoding='utf-8') as f:
        attrs = json.load(f)

    print(f"Processing {len(attrs)} products...")
    
    updates = []
    for item in attrs:
        oid = item.get('offer_id')
        cat_id = item.get('description_category_id')
        type_id = item.get('type_id')
        
        # Find Title inside current attributes
        current_name = ""
        current_name_attr = None
        for a in item.get('attributes', []):
            if a.get('id') in [4180, 4191]:
                current_name = a.get('values', [{}])[0].get('value', '')
                current_name_attr = a.get('id')
                break
        
        if not current_name:
            # Fallback to product info name if hidden in attrs
            # (though info/attributes should return it)
            continue
            
        new_name = expand_title(current_name)
        new_tags = generate_hashtags(new_name)
        
        # Prepare attributes for update
        update_attrs = []
        
        # 1. Update Title (if changed)
        if new_name != current_name:
            update_attrs.append({"id": current_name_attr, "values": [{"value": new_name}]})
            
        # 2. Add Hashtags (Keywords attr 23171)
        update_attrs.append({"id": 23171, "values": [{"value": new_tags}]})
        
        updates.append({
            "description_category_id": cat_id,
            "type_id": type_id,
            "offer_id": oid,
            "attributes": update_attrs
        })

    print(f"Applying updates for {len(updates)} products...")
    
    # Ozon allows 20 items per request in /v1/product/attributes/update
    BATCH_SIZE = 10 
    ok = 0
    err = 0
    for i in range(0, len(updates), BATCH_SIZE):
        batch = updates[i:i+BATCH_SIZE]
        body = {"items": batch}
        r = requests.post("https://api-seller.ozon.ru/v1/product/attributes/update", headers=H, json=body, timeout=30)
        
        if r.status_code == 200:
            ok += len(batch)
            print(f"  Success: {i+len(batch)}/{len(updates)}")
        else:
            err += len(batch)
            print(f"  Error at index {i}: {r.status_code} {r.text[:200]}")
        time.sleep(1)

    print(f"\nFINISH: {ok} OK, {err} ERR")

if __name__ == "__main__":
    apply_seo()
