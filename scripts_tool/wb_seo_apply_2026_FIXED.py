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

print(f"Starting SEO Optimization for {len(cards_data)} cards...")

def get_optimized_title(card: Dict[str, Any]) -> str:
    old_title: str = str(card.get('title', ''))
    vc: str = str(card.get('vendorCode', '')).lower()
    keywords = "гравировка 2026"
    category = "Браслет"
    
    tl_lower = old_title.lower()
    if 'именной' in tl_lower or 'именной' in vc:
        category = "Именной с гравировкой"
    elif 'зодиак' in tl_lower or 'зодиак' in vc:
        category = "Браслет Зодиак гравировка"
    elif 'армия' in tl_lower or 'армия' in vc:
        category = "Армия на службу именной"
        
    clean_title = old_title
    generic_names = ["Именной", "Армия", "Зодиак", "Именной с гравировкой"]
    if old_title.lower().strip() in [g.lower() for g in generic_names]:
        clean_title = "" 
        
    # Strict 60 char limit for jewelry
    new_title = f"{category} {clean_title} {keywords}".strip().replace("  ", " ")
    
    final_title_str = str(new_title)
    if len(final_title_str) > 60:
        truncated_title = str(final_title_str)[:57]
        final_title_str = f"{truncated_title}..."
    return final_title_str

def get_optimized_desc(card: Dict[str, Any]) -> str:
    old_desc: str = str(card.get('description', ''))
    if "Популярные именной браслет гравировка в 2026-2027" in old_desc:
        return old_desc
        
    intro = "Эксклюзивный браслет ўЂ" именной бренда премиум качество с гравировкой в современном стиле у производителя 2025 года ўЂ" года Змеи. Изделие добавляет элегантность и индивидуальность в образ из нержавеющей стали 316L (медицинская сталь)."
    body = (
        "\n\nПопулярные именной браслет персональная гравировка в 2026-2027 года:?\n"
        "- Индивидуальная гравировка: На изделие наносятся специализированная лазерная гравировка имени, даты или имён.\n"
        "- Эмоциональная ценность: Превращает браслет именной в личную память или символ важной даты, для себя, на подарок и не только.\n"
        "- Подарок с историей: Подходит для подарка на день 2026, 23 февраля или День Рождения.\n"
        "- Стильный дизайн: Минималистичный дизайн, удобный подарочный упаковка индивидуальностью."
    )
    outro = "\n\nПодарок всегда в памяти. Персональная подарок с поддержкой."
    
    new_desc = f"{intro}\n\n{old_desc}{body}{outro}"
    desc_str = str(new_desc)
    if len(desc_str) > 5000:
        truncated_desc = str(desc_str)[:4990]
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

# BATCH PROCESSING - API expects array of cards
BATCH_SIZE = 100  # Can be up to 3000, but we use 100 for better error handling
remaining_cards = [c for c in cards_data if c.get('nmID') is not None and c.get('nmID') not in done_ids]

total_batches = (len(remaining_cards) + BATCH_SIZE - 1) // BATCH_SIZE
print(f"Processing {len(remaining_cards)} cards in {total_batches} batches...")

for batch_idx in range(0, len(remaining_cards), BATCH_SIZE):
    batch_cards = remaining_cards[batch_idx:batch_idx + BATCH_SIZE]
    batch_payload = []
    batch_nm_ids = []
    
    for c in batch_cards:
        nm_id = c.get('nmID')
        new_title = get_optimized_title(c)
        new_desc = get_optimized_desc(c)
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
        
        batch_payload.append(card_body)
        batch_nm_ids.append(nm_id)
    
    # Send batch request
    retries = 3
    success = False
    current_batch = batch_idx // BATCH_SIZE + 1
    
    while retries > 0:
        try:
            # CRITICAL FIX: Send array of cards
            r = requests.post(UPDATE_URL, headers=headers, json=batch_payload, timeout=60)
            
            if r.status_code == 200:
                resp_json = r.json()
                if resp_json.get('error'):
                    print(f"[Batch {current_batch}/{total_batches}] VALIDATION ERROR: {resp_json.get('errorText')}")
                    # Even with error, mark as processed to avoid infinite loop
                    break
                    
                print(f"[Batch {current_batch}/{total_batches}] SUCCESS: {len(batch_nm_ids)} cards updated")
                print(f"  Sample NM_IDs: {batch_nm_ids[:5]}")
                
                # Mark all as done
                for nm_id in batch_nm_ids:
                    done_ids.add(int(nm_id))
                
                with open(PROGRESS_FILE, 'w') as f:
                    json.dump(list(done_ids), f)
                    
                success = True
                break
                
            elif r.status_code == 429:
                print(f"[Batch {current_batch}/{total_batches}] RATE LIMITED. Sleeping 40s...")
                time.sleep(40)
                retries -= 1
                
            else:
                print(f"[Batch {current_batch}/{total_batches}] HTTP ERROR {r.status_code}: {r.text[:200]}")
                break
                
        except Exception as e:
            print(f"[Batch {current_batch}/{total_batches}] EXCEPTION: {e}")
            time.sleep(10)
            retries -= 1
    
    # Rate limit compliance: 10 requests per minute = 6 seconds between requests
    if batch_idx + BATCH_SIZE < len(remaining_cards):
        time.sleep(7.0)

print(f"\nFinal completion! Processed {len(done_ids)} cards total.")
print("Check errors at: https://seller.wildberries.ru/new-goods/error-cards")
