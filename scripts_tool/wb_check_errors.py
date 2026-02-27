# -*- coding: utf-8 -*-
"""
ПРОВЕРКА СОСТОЯНИЯ КАРТОЧЕК WB И АНАЛИЗ ЧЕРНОВИКОВ
"""
import json
import os
import requests
from typing import List, Dict, Any
from collections import defaultdict

BASE_DIR = r'C:\Users\GravMix\.gemini\antigravity\playground\core-pulsar'
ENV_PATH = os.path.join(BASE_DIR, '.env')

# Загрузка API ключа
WB_KEY = ''
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('WB_API_KEY='):
                WB_KEY = line.strip().split('=', 1)[1]
                break

if not WB_KEY:
    print("❌ WB_API_KEY not found")
    exit(1)

headers = {'Authorization': WB_KEY, 'Content-Type': 'application/json'}

print("╔══════════════════════════════════════════════════════════════╗")
print("║         ПРОВЕРКА КАРТОЧЕК И ЧЕРНОВИКОВ WILDBERRIES           ║")
print("╚══════════════════════════════════════════════════════════════╝\n")

# 1. Проверка черновиков (ошибочных карточек)
print("🔍 1. ПРОВЕРКА ЧЕРНОВИКОВ (ERROR CARDS)")
print("─" * 60)

error_url = 'https://content-api.wildberries.ru/content/v2/cards/error/list'
error_payload = {
    "cursor": {"limit": 100},
    "order": {"ascending": False}
}

try:
    r = requests.post(error_url, headers=headers, json=error_payload, timeout=30)
    if r.status_code == 200:
        error_data = r.json()
        
        if error_data.get('data') and error_data['data'].get('items'):
            items = error_data['data']['items']
            print(f"❌ Найдено проблемных пакетов: {len(items)}\n")
            
            total_errors = 0
            for idx, item in enumerate(items[:10], 1):  # Показываем первые 10
                vendor_codes = item.get('vendorCodes', [])
                errors = item.get('errors', {})
                
                print(f"Пакет #{idx}:")
                print(f"  Артикулов: {len(vendor_codes)}")
                
                # Показываем ошибки
                for vc in vendor_codes[:3]:  # Первые 3 артикула
                    if vc in errors:
                        print(f"  • {vc}:")
                        for err in errors[vc][:2]:  # Первые 2 ошибки
                            print(f"    - {err}")
                        total_errors += len(errors[vc])
                print()
            
            print(f"Всего ошибок: {total_errors}")
        else:
            print("✓ Черновиков не найдено!")
    else:
        print(f"❌ Ошибка API: {r.status_code}")
except Exception as e:
    print(f"❌ Exception: {e}")

print("\n" + "="*60 + "\n")

# 2. Проверка текущих карточек
print("📋 2. ПРОВЕРКА АКТИВНЫХ КАРТОЧЕК")
print("─" * 60)

cards_url = 'https://content-api.wildberries.ru/content/v2/get/cards/list'
cards_payload = {
    "settings": {
        "cursor": {"limit": 100},
        "filter": {"withPhoto": -1}
    }
}

try:
    r = requests.post(cards_url, headers=headers, json=cards_payload, timeout=30)
    if r.status_code == 200:
        cards_data = r.json()
        cards = cards_data.get('cards', [])
        
        print(f"Найдено активных карточек: {len(cards)}\n")
        
        # Анализ проблем
        issues = {
            'no_photos': 0,
            'few_photos': 0,
            'few_chars': 0,
            'short_title': 0,
            'short_desc': 0
        }
        
        for card in cards:
            photos = len(card.get('photos', []))
            if photos == 0:
                issues['no_photos'] += 1
            elif photos < 4:
                issues['few_photos'] += 1
            
            chars = len(card.get('characteristics', []))
            if chars < 5:
                issues['few_chars'] += 1
            
            title = card.get('title', '')
            if len(title) < 20:
                issues['short_title'] += 1
            
            desc = card.get('description', '')
            if len(desc) < 500:
                issues['short_desc'] += 1
        
        print("Проблемы активных карточек:")
        print(f"  • Нет фото: {issues['no_photos']}")
        print(f"  • Мало фото (<4): {issues['few_photos']}")
        print(f"  • Мало характеристик (<5): {issues['few_chars']}")
        print(f"  • Короткий заголовок (<20): {issues['short_title']}")
        print(f"  • Короткое описание (<500): {issues['short_desc']}")
        
        # Сохраняем для дальнейшего анализа
        with open(os.path.join(BASE_DIR, 'wb_current_state.json'), 'w', encoding='utf-8') as f:
            json.dump({
                'total_cards': len(cards),
                'issues': issues,
                'cards': cards[:50]  # Первые 50 для примера
            }, f, ensure_ascii=False, indent=2)
    else:
        print(f"❌ Ошибка API: {r.status_code}")
except Exception as e:
    print(f"❌ Exception: {e}")

print("\n✓ Проверка завершена!")
print(f"Детали сохранены: wb_current_state.json")
