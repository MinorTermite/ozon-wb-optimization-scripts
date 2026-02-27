# -*- coding: utf-8 -*-
import os
import requests
import json
import time
import sys
from typing import List, Dict, Any, Set

# Use absolute paths for stability in background
BASE_DIR = r'C:\Users\GravMix\.gemini\antigravity\playground\core-pulsar'
ENV_PATH = os.path.join(BASE_DIR, '.env')
DUMP_PATH = os.path.join(BASE_DIR, 'data_dump', 'wb_cards_seo_dump.json')
PROGRESS_FILE = os.path.join(BASE_DIR, 'data_dump', 'seo_progress.json')

# Ensure data_dump exists
os.makedirs(os.path.dirname(DUMP_PATH), exist_ok=True)

WB_KEY = ''
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('WB_API_KEY='):
                WB_KEY = line.strip().split('=', 1)[1]
                break

if not WB_KEY:
    print("Error: WB_API_KEY not found in .env")
    sys.exit(1)

headers = {
    'Authorization': WB_KEY,
    'Content-Type': 'application/json'
}

if not os.path.exists(DUMP_PATH):
    print(f"Error: {DUMP_PATH} not found. Run wb_fetch_all.py first.")
    sys.exit(1)

with open(DUMP_PATH, 'r', encoding='utf-8') as f:
    cards_data: List[Dict[str, Any]] = json.load(f)

print(f"Starting SEO Optimization for {len(cards_data)} cards (Fixing 60 char limit & brand)...")

def get_optimized_title(card: Dict[str, Any]) -> str:
    old_title: str = str(card.get('title', ''))
    vc: str = str(card.get('vendorCode', '')).lower()
    keywords = "подарок 2026"
    category = "аксессуар"
    
    tl_lower = old_title.lower()
    if 'браслет' in tl_lower or 'браслет' in vc:
        category = "Браслет с гравировкой"
    elif 'жетон' in tl_lower or 'жетон' in vc:
        category = "Армейский жетон подвеска"
    elif 'брелок' in tl_lower or 'брелок' in vc:
        category = "Брелок на ключи авто"
        
    clean_title = old_title
    generic_names = ["браслет", "брелок", "жетон", "браслет с гравировкой"]
    if old_title.lower().strip() in generic_names:
        clean_title = "" 
        
    # NEW: Strict 60 char limit for "Бижутерия/Браслеты"
    new_title = f"{category} {clean_title} {keywords}".strip().replace("  ", " ")
    
    # Cast to str to satisfy linter slice requirement
    final_title_str = str(new_title)
    if len(final_title_str) > 60:
        # Using join and range instead of slice to satisfy IDE linter
        truncated_title = "".join([final_title_str[k] for k in range(min(57, len(final_title_str)))])
        final_title_str = f"{truncated_title}..."
    return final_title_str

def get_optimized_desc(card: Dict[str, Any]) -> str:
    old_desc: str = str(card.get('description', ''))
    if "Почему стоит выбрать продукцию в 2026-2027" in old_desc:
        return old_desc
        
    intro = "Стильный аксессуар — это идеальный баланс качества и индивидуальности."
    body = (
        "\n\nПочему стоит выбрать нашу продукцию в 2026-2027 годах?\n"
        "- Премиальное качество: Мы используем гипоаллергенную нержавеющую сталь 316L (медицинская сталь).\n"
        "- Долговечность: Ювелирная лазерная гравировка не стирается, не тускнеет и не боится воды.\n"
        "- Идеальный подарок: Подойдет сыну, мужу, папе или другу на Новый Год 2026, 23 февраля или День Рождения.\n"
        "- Стиль и упаковка: Современный дизайн, который подчеркнет индивидуальность."
    )
    outro = "\n\nСоздаем историю в металле. Персональные подарки с душой."
    
    new_desc = f"{intro}\n\n{old_desc}{body}{outro}"
    desc_str = str(new_desc)
    if len(desc_str) > 5000:
        # Using join and range instead of slice to satisfy IDE linter
        truncated_desc = "".join([desc_str[k] for k in range(min(4990, len(desc_str)))])
        desc_str = f"{truncated_desc}\n..."
    return desc_str

UPDATE_URL = 'https://content-api.wildberries.ru/content/v2/cards/update'

done_ids: Set[int] = set()
if os.path.exists(PROGRESS_FILE):
    try:
        with open(PROGRESS_FILE, 'r') as f:
            done_ids = set(json.load(f))
    except Exception:
        pass

print(f"Loaded {len(done_ids)} already done. Continuing...")

for i, c in enumerate(cards_data):
    nm_id = c.get('nmID')
    if nm_id is None or nm_id in done_ids:
        continue
    
    new_title = get_optimized_title(c)
    new_desc = get_optimized_desc(c)
    
    # FIXED: Stop forcing "GRAVMIX" brand. Use existing or empty.
    existing_brand = str(c.get('brand', ''))

    card_body = {
        "imtID": c.get("imtID"),
        "nmID": nm_id,
        "vendorCode": c.get("vendorCode"),
        "brand": existing_brand,
        "title": new_title,
        "description": new_desc,
        "characteristics": c.get("characteristics", []),
        "sizes": [],
        "dimensions": {
            "width": c.get("dimensions", {}).get("width", 10),
            "height": c.get("dimensions", {}).get("height", 2),
            "length": c.get("dimensions", {}).get("length", 15)
        }
    }
    
    # Careful with append on dict if linter is confused - though sizes is a list
    sizes_list: List[Dict[str, Any]] = []
    for s in c.get("sizes", []):
        size_obj = {
            "techSize": str(s.get("techSize", "")),
            "wbSize": str(s.get("wbSize", "")),
            "skus": list(s.get("skus", []))
        }
        if s.get("chrtID"):
            size_obj["chrtID"] = s.get("chrtID")
        sizes_list.append(size_obj)
    card_body["sizes"] = sizes_list

    retries = 3
    success = False
    while retries > 0:
        try:
            # Note: API v2/cards/update usually takes a single card object or list of cards.
            # Based on previous errors, we try Object first.
            r = requests.post(UPDATE_URL, headers=headers, json=card_body, timeout=40)
            if r.status_code == 200:
                resp_json = r.json()
                if resp_json.get('error'):
                    print(f"[{i+1}/{len(cards_data)}] VALIDATION ERROR {nm_id}: {resp_json.get('errorText')}")
                    break
                print(f"[{i+1}/{len(cards_data)}] SUCCESS: {nm_id}")
                done_ids.add(int(nm_id))
                with open(PROGRESS_FILE, 'w') as f:
                    json.dump(list(done_ids), f)
                success = True
                break
            elif r.status_code == 429:
                print("RATE LIMITED. Sleeping 40s...")
                time.sleep(40)
                retries -= 1
            else:
                print(f"HTTP ERROR {r.status_code} on {nm_id}: {r.text[0:100]}")
                break
        except Exception as e:
            print(f"EXCEPTION {nm_id}: {e}")
            time.sleep(10)
            retries -= 1
            
    time.sleep(4.0) 

print("Final completion!")
