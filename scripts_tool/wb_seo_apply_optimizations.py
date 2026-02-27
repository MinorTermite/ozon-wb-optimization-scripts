# -*- coding: utf-8 -*-
"""
ПРИМЕНЕНИЕ SEO ОПТИМИЗАЦИЙ К WILDBERRIES
Обновляет карточки оптимизированными версиями
"""
import json
import os
import requests
import time
from typing import List, Dict, Any

BASE_DIR = r'C:\Users\GravMix\.gemini\antigravity\playground\core-pulsar'
ENV_PATH = os.path.join(BASE_DIR, '.env')
DUMP_PATH = os.path.join(BASE_DIR, 'data_dump', 'wb_cards_seo_dump.json')
OPTIMIZED_PATH = os.path.join(BASE_DIR, 'WB_SEO_OPTIMIZED_CARDS.json')
PROGRESS_FILE = os.path.join(BASE_DIR, 'data_dump', 'seo_optimization_progress.json')

# Загрузка API ключа
WB_KEY = ''
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('WB_API_KEY='):
                WB_KEY = line.strip().split('=', 1)[1]
                break

if not WB_KEY:
    print("❌ Error: WB_API_KEY not found in .env")
    exit(1)

headers = {
    'Authorization': WB_KEY,
    'Content-Type': 'application/json'
}

# Загрузка данных
with open(DUMP_PATH, 'r', encoding='utf-8') as f:
    cards = json.load(f)

with open(OPTIMIZED_PATH, 'r', encoding='utf-8') as f:
    optimized = json.load(f)

# Создаем словарь карточек
cards_dict = {c['nmID']: c for c in cards}
optimized_dict = {o['nm_id']: o for o in optimized['cards']}

print(f"╔══════════════════════════════════════════════════════════════╗")
print(f"║  ПРИМЕНЕНИЕ SEO ОПТИМИЗАЦИЙ К WILDBERRIES                    ║")
print(f"║  Карточек к обновлению: {len(optimized['cards']):3d}                            ║")
print(f"╚══════════════════════════════════════════════════════════════╝\n")

# Загрузка прогресса
done_ids = set()
if os.path.exists(PROGRESS_FILE):
    try:
        with open(PROGRESS_FILE, 'r') as f:
            done_ids = set(json.load(f))
    except:
        pass

print(f"Уже оптимизировано: {len(done_ids)} карточек\n")

UPDATE_URL = 'https://content-api.wildberries.ru/content/v2/cards/update'
BATCH_SIZE = 50  # Меньший размер для большей точности

remaining = [nm_id for nm_id in optimized_dict.keys() if nm_id not in done_ids]

if not remaining:
    print("✓ Все карточки уже оптимизированы!")
    exit(0)

total_batches = (len(remaining) + BATCH_SIZE - 1) // BATCH_SIZE
print(f"Обработка {len(remaining)} карточек в {total_batches} пакетах...\n")

success_count = 0
error_count = 0

for batch_idx in range(0, len(remaining), BATCH_SIZE):
    batch_ids = remaining[batch_idx:batch_idx + BATCH_SIZE]
    batch_payload = []
    
    for nm_id in batch_ids:
        original_card = cards_dict.get(nm_id)
        optimized_card = optimized_dict.get(nm_id)
        
        if not original_card or not optimized_card:
            continue
        
        card_body = {
            "imtID": original_card.get("imtID"),
            "nmID": nm_id,
            "vendorCode": original_card.get("vendorCode"),
            "brand": original_card.get("brand", ""),
            "title": optimized_card['new_title'],
            "description": optimized_card['new_description'],
            "characteristics": original_card.get("characteristics", []),
            "dimensions": {
                "width": original_card.get("dimensions", {}).get("width", 10),
                "height": original_card.get("dimensions", {}).get("height", 2),
                "length": original_card.get("dimensions", {}).get("length", 15)
            },
            "sizes": []
        }
        
        # Копируем размеры
        for s in original_card.get("sizes", []):
            size_obj = {
                "techSize": str(s.get("techSize", "")),
                "wbSize": str(s.get("wbSize", "")),
                "skus": list(s.get("skus", []))
            }
            if s.get("chrtID"):
                size_obj["chrtID"] = s.get("chrtID")
            card_body["sizes"].append(size_obj)
        
        batch_payload.append(card_body)
    
    # Отправка пакета
    current_batch = batch_idx // BATCH_SIZE + 1
    retries = 3
    
    while retries > 0:
        try:
            r = requests.post(UPDATE_URL, headers=headers, json=batch_payload, timeout=60)
            
            if r.status_code == 200:
                resp = r.json()
                if not resp.get('error'):
                    print(f"[Batch {current_batch}/{total_batches}] ✓ SUCCESS: {len(batch_ids)} cards")
                    success_count += len(batch_ids)
                    
                    # Сохраняем прогресс
                    for nm_id in batch_ids:
                        done_ids.add(nm_id)
                    
                    with open(PROGRESS_FILE, 'w') as f:
                        json.dump(list(done_ids), f)
                    break
                else:
                    print(f"[Batch {current_batch}/{total_batches}] ⚠ API Error: {resp.get('errorText')}")
                    error_count += len(batch_ids)
                    break
                    
            elif r.status_code == 429:
                print(f"[Batch {current_batch}/{total_batches}] Rate limit, waiting...")
                time.sleep(40)
                retries -= 1
            else:
                print(f"[Batch {current_batch}/{total_batches}] ❌ HTTP {r.status_code}")
                error_count += len(batch_ids)
                break
                
        except Exception as e:
            print(f"[Batch {current_batch}/{total_batches}] ❌ Exception: {e}")
            retries -= 1
            if retries > 0:
                time.sleep(10)
    
    # Rate limit compliance
    if batch_idx + BATCH_SIZE < len(remaining):
        time.sleep(7.0)

print(f"\n{'='*60}")
print(f"ИТОГИ ОПТИМИЗАЦИИ:")
print(f"✓ Успешно обновлено: {success_count} карточек")
print(f"❌ Ошибок: {error_count} карточек")
print(f"📊 Всего обработано: {len(done_ids)} из {len(optimized['cards'])}")
print(f"{'='*60}")

if success_count > 0:
    print(f"\n⏰ Изменения будут синхронизированы в течение 30 минут")
    print(f"🔍 Проверьте результат: https://seller.wildberries.ru/goods/list")
