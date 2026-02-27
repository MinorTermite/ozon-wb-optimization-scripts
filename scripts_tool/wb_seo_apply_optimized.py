# -*- coding: utf-8 -*-
"""
ПРИМЕНЕНИЕ SEO ОПТИМИЗАЦИЙ НА WILDBERRIES
Загружает оптимизированные карточки и применяет через API v2
"""
import os, json, requests, time, sys
from typing import List, Dict, Set

BASE = r'C:\Users\GravMix\.gemini\antigravity\playground\core-pulsar'
ENV = os.path.join(BASE, '.env')
OPTIMIZED = os.path.join(BASE, 'data_dump', 'wb_cards_optimized_full.json')
PROGRESS = os.path.join(BASE, 'data_dump', 'seo_optimization_progress.json')

# Загрузка API ключа
WB_KEY = ''
if os.path.exists(ENV):
    with open(ENV, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('WB_API_KEY='):
                WB_KEY = line.strip().split('=', 1)[1]
                break

if not WB_KEY:
    print("❌ Ошибка: WB_API_KEY не найден в .env")
    sys.exit(1)

headers = {
    'Authorization': WB_KEY,
    'Content-Type': 'application/json'
}

UPDATE_URL = 'https://content-api.wildberries.ru/content/v2/cards/update'

# Загрузка оптимизированных карточек
print("📦 Загрузка оптимизированных карточек...")
with open(OPTIMIZED, encoding='utf-8-sig') as f:
    cards = json.load(f)
print(f"✓ Загружено: {len(cards)} карточек\n")

# Загрузка прогресса
done_ids = set()
if os.path.exists(PROGRESS):
    try:
        with open(PROGRESS) as f:
            done_ids = set(json.load(f))
    except:
        pass

print(f"Уже обработано: {len(done_ids)} карточек")
remaining = [c for c in cards if c.get('nmID') not in done_ids]
print(f"Осталось обработать: {len(remaining)} карточек\n")

# Пакетная обработка
BATCH_SIZE = 100
total_batches = (len(remaining) + BATCH_SIZE - 1) // BATCH_SIZE

print(f"🚀 Начинаем применение SEO оптимизаций...")
print(f"Пакетов: {total_batches} x {BATCH_SIZE} карточек\n")

for batch_idx in range(0, len(remaining), BATCH_SIZE):
    batch = remaining[batch_idx:batch_idx + BATCH_SIZE]
    batch_payload = []
    batch_nm_ids = []
    
    for card in batch:
        nm_id = card.get('nmID')
        
        # Формируем payload с оптимизированными данными
        card_body = {
            "imtID": card.get("imtID"),
            "nmID": nm_id,
            "vendorCode": card.get("vendorCode"),
            "brand": card.get("brand_optimized", "GRAVMIX"),
            "title": card.get("title_optimized"),
            "description": card.get("description_optimized"),
            "characteristics": card.get("characteristics", []),
            "sizes": [],
            "dimensions": {
                "width": card.get("dimensions", {}).get("width", 10),
                "height": card.get("dimensions", {}).get("height", 2),
                "length": card.get("dimensions", {}).get("length", 15)
            }
        }
        
        # Sizes
        for s in card.get("sizes", []):
            size_obj = {
                "techSize": str(s.get("techSize", "")),
                "wbSize": str(s.get("wbSize", "")),
                "skus": list(s.get("skus", []))
            }
            if s.get("chrtID"):
                size_obj["chrtID"] = s.get("chrtID")
            card_body["sizes"].append(size_obj)
        
        batch_payload.append(card_body)
        batch_nm_ids.append(nm_id)
    
    # Отправка пакета
    current_batch = batch_idx // BATCH_SIZE + 1
    retries = 3
    
    while retries > 0:
        try:
            r = requests.post(UPDATE_URL, headers=headers, json=batch_payload, timeout=60)
            
            if r.status_code == 200:
                resp = r.json()
                if resp.get('error'):
                    print(f"[Пакет {current_batch}/{total_batches}] ⚠️ Ошибка валидации: {resp.get('errorText')}")
                    break
                
                print(f"[Пакет {current_batch}/{total_batches}] ✅ УСПЕХ: {len(batch_nm_ids)} карточек оптимизировано")
                
                # Сохранение прогресса
                for nm_id in batch_nm_ids:
                    done_ids.add(int(nm_id))
                
                with open(PROGRESS, 'w') as f:
                    json.dump(list(done_ids), f)
                
                break
                
            elif r.status_code == 429:
                print(f"[Пакет {current_batch}/{total_batches}] ⏳ Rate limit. Пауза 40 сек...")
                time.sleep(40)
                retries -= 1
                
            else:
                print(f"[Пакет {current_batch}/{total_batches}] ❌ HTTP {r.status_code}: {r.text[:100]}")
                break
                
        except Exception as e:
            print(f"[Пакет {current_batch}/{total_batches}] ❌ Ошибка: {e}")
            time.sleep(10)
            retries -= 1
    
    # Пауза между пакетами (rate limit compliance)
    if batch_idx + BATCH_SIZE < len(remaining):
        time.sleep(7.0)

print(f"\n{'='*60}")
print(f"✅ СЕО ОПТИМИЗАЦИЯ ЗАВЕРШЕНА!")
print(f"{'='*60}")
print(f"📊 Обработано: {len(done_ids)} карточек")
print(f"📁 Прогресс: {PROGRESS}")
print(f"\n⏱ Синхронизация с WB: до 30 минут")
print(f"🔗 Проверка ошибок: https://seller.wildberries.ru/new-goods/error-cards")
