import requests
import json
import time

H = {
    'Client-Id': '311191',
    'Api-Key': '88da03d6-8f00-4189-af6b-db145ec7689f',
    'Content-Type': 'application/json'
}

def apply_final_fixes():
    print("Loading data...")
    with open('ozon2_active_attributes.json', 'r', encoding='utf-8') as f:
        attrs = json.load(f)

    updates = []
    for item in attrs:
        oid = item.get('offer_id')
        cat_id = item.get('description_category_id')
        type_id = item.get('type_id')
        name = ""
        # Find name in attributes to use for logic
        for a in item.get('attributes', []):
            if a.get('id') in [4180, 4191]:
                name = a.get('values', [{}])[0].get('value', '').lower()
                break
        
        # 1. Base Attributes (Audience, Gender, Material)
        # 9390: Audience (43241 - Взрослая)
        # 9163: Gender (22880 - Мужской) - mostly male gifts
        # 5309: Material (972088542 - Ювелирная сталь, 971202939 - Кожа, 61936 - Металл)
        
        target_audience = 43241
        target_gender = 22880
        if "жен" in name or "маме" in name or "доче" in name:
            target_gender = 22881
            
        target_material = 972088542 # Default: Steel
        if "кож" in name:
            target_material = 971202939 # Leather
        elif "брелок" in name and "кож" not in name:
            target_material = 61936 # Metal
            
        # 2. Grouping (Model Name Attr 9048)
        model_name = ""
        if "знак зодиака" in name or any(z in name for z in ["овен", "телец", "близнецы", "рак", "лев", "дева", "весы", "скорпион", "стрелец", "козерог", "водолей", "рыбы"]):
            if "браслет" in name: model_name = "Браслет кожаный Знаки Зодиака GRAVMIX"
            else: model_name = "Жетон Знаки Зодиака GRAVMIX"
        elif "жетон" in name:
            if "армей" in name or "вдв" in name or "погран" in name:
                model_name = "Армейский жетон с гравировкой GRAVMIX"
        elif "браслет" in name:
            if "любимому" in name or "муж" in name:
                model_name = "Браслет кожаный Подарок Мужчине GRAVMIX"
            else:
                model_name = "Браслет кожаный с гравировкой GRAVMIX"
        elif "брелок" in name:
            if "авто" in name or "логотип" in name:
                model_name = "Брелок автомобильный GRAVMIX"
            else:
                model_name = "Брелок для ключей GRAVMIX"

        # Prepare attributes
        u_attrs = [
            {"id": 9390, "values": [{"dictionary_value_id": target_audience}]},
            {"id": 9163, "values": [{"dictionary_value_id": target_gender}]},
            {"id": 5309, "values": [{"dictionary_value_id": target_material}]}
        ]
        if model_name:
            u_attrs.append({"id": 9048, "values": [{"value": model_name}]})

        updates.append({
            "description_category_id": cat_id,
            "type_id": type_id,
            "offer_id": oid,
            "attributes": u_attrs
        })

    print(f"Applying updates to {len(updates)} products...")
    BATCH_SIZE = 10
    ok, err = 0, 0
    for i in range(0, len(updates), BATCH_SIZE):
        batch = updates[i:i+BATCH_SIZE]
        r = requests.post("https://api-seller.ozon.ru/v1/product/attributes/update", headers=H, json={"items": batch})
        if r.status_code == 200:
            ok += len(batch)
            print(f"  Processed {i+len(batch)}/{len(updates)}")
        else:
            err += len(batch)
            print(f"  Error at {i}: {r.status_code} {r.text[:200]}")
        time.sleep(1)
        
    print(f"FINISH: {ok} OK, {err} ERR")

if __name__ == "__main__":
    apply_final_fixes()
