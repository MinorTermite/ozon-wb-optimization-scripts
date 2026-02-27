# -*- coding: utf-8 -*-
import json, os, requests, sys
BASE_DIR = r'C:\Users\GravMix\.gemini\antigravity\playground\core-pulsar'
ENV_PATH = os.path.join(BASE_DIR, '.env')
VALIDATION_DIR = os.path.join(BASE_DIR, 'validation_report')
os.makedirs(VALIDATION_DIR, exist_ok=True)
WB_KEY = ''
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('WB_API_KEY='):
                WB_KEY = line.strip().split('=', 1)[1]
                break
if not WB_KEY:
    print("❌ Error: WB_API_KEY not found")
    sys.exit(1)
headers = {'Authorization': WB_KEY, 'Content-Type': 'application/json'}
print("╔══════════════════════════════════════════════════════════════╗")
print("║  ГЛУБОКАЯ ПРОВЕРКА ОШИБОК WB - GRAVMIX                       ║")
print("╚══════════════════════════════════════════════════════════════╝\n")
print("📋 1. ЗАГРУЗКА КАРТОЧЕК...")
CARDS_URL = 'https://content-api.wildberries.ru/content/v2/get/cards/list'
r = requests.post(CARDS_URL, headers=headers, json={"settings": {"cursor": {"limit": 1000}, "filter": {"withPhoto": -1}}}, timeout=30)
all_cards = r.json().get('cards', []) if r.status_code == 200 else []
print(f"✓ Карточек: {len(all_cards)}\n")
print("🔍 2. ПРОВЕРКА ОШИБОК ВАЛИДАЦИИ...")
ERROR_URL = 'https://content-api.wildberries.ru/content/v2/cards/error/list'
r2 = requests.get(ERROR_URL, headers=headers, timeout=30)
val_errors = r2.json().get('data', []) if r2.status_code == 200 and r2.json() else []
print(f"⚠️ Ошибок валидации: {len(val_errors)}\n")
if val_errors:
    err_types = {}
    for e in val_errors:
        et = e.get('errors', ['Unknown'])[0] if e.get('errors') else 'Unknown'
        err_types[et] = err_types.get(et, 0) + 1
    for et, cnt in err_types.items():
        print(f"  • {et}: {cnt}")
print("\n📊 3. ПРОВЕРКА ПОЛЕЙ...")
issues = {'long_title':[],'no_brand':[],'wrong_brand':[],'zero_dims':[],'no_weight':[],'low_rating':[],'few_photos':[]}
for c in all_cards:
    nm = c.get('nmID')
    t = c.get('title','')
    if len(t) > 50: issues['long_title'].append({'nm':nm,'title':t,'len':len(t)})
    b = c.get('brand','')
    if not b: issues['no_brand'].append(nm)
    elif b.lower() != 'gravmix': issues['wrong_brand'].append({'nm':nm,'brand':b})
    d = c.get('dimensions',{})
    if d.get('width',0)==0 or d.get('height',0)==0 or d.get('length',0)==0: issues['zero_dims'].append({'nm':nm,'dims':d})
    chs = c.get('characteristics',[])
    if not any(ch.get('id')==14177450 for ch in chs): issues['no_weight'].append(nm)
    r = c.get('rating',0)
    if r>0 and r<4.0: issues['low_rating'].append({'nm':nm,'rating':r,'vc':c.get('vendorCode')})
    if len(c.get('photos',[])) < 4: issues['few_photos'].append({'nm':nm,'cnt':len(c.get('photos',[]))})
print(f"🔴 КРИТИЧНО:")
print(f"  Заголовки >50: {len(issues['long_title'])}")
print(f"  Рейтинг <4.0: {len(issues['low_rating'])} (КЛОНИРОВАТЬ!)")
print(f"  Нулевые габариты: {len(issues['zero_dims'])}")
print(f"  Нет веса: {len(issues['no_weight'])}")
print(f"\n🟡 ВАЖНО:")
print(f"  Неправильный бренд: {len(issues['wrong_brand'])}")
print(f"  Нет бренда: {len(issues['no_brand'])}")
print(f"  Мало фото: {len(issues['few_photos'])}\n")
if issues['low_rating']:
    print("🎯 КЛОНИРОВАТЬ (рейтинг <4.0):")
    for i in issues['low_rating'][:15]:
        print(f"  NM_{i['nm']} ({i['vc']}) - {i['rating']:.1f}")
    print()
if issues['long_title']:
    print("📏 ЗАГОЛОВКИ >50 символов:")
    for i in issues['long_title'][:5]:
        print(f"  NM_{i['nm']} ({i['len']}): {i['title'][:60]}...")
    print()
rep = {'total':len(all_cards),'val_errors':len(val_errors),'issues':{k:len(v) for k,v in issues.items()},'details':issues,'api_errors':val_errors[:30]}
with open(os.path.join(VALIDATION_DIR, 'wb_validation_report.json'), 'w', encoding='utf-8') as f:
    json.dump(rep, f, ensure_ascii=False, indent=2)
print(f"{'='*70}")
print("🚨 ПРИОРИТЕТЫ:")
print(f"1. 🔴 КЛОНИРОВАТЬ {len(issues['low_rating'])} карточек <4.0")
print(f"2. 🔴 СОКРАТИТЬ {len(issues['long_title'])} заголовков до 50")
print(f"3. 🔴 ИСПРАВИТЬ {len(issues['zero_dims'])} нулевых габаритов")
print(f"4. 🟡 ДОБАВИТЬ вес {len(issues['no_weight'])} карточкам")
print(f"5. 🟡 ИСПРАВИТЬ {len(issues['wrong_brand'])} брендов")
print(f"\n✓ Отчет: validation_report/wb_validation_report.json")
