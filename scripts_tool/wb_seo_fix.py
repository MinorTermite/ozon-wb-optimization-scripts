# -*- coding: utf-8 -*-
"""
WB Complete Fix: fill missing characteristics + fix descriptions + titles
Sends FULL card data including sizes to avoid validation errors
Rate limit: 3 seconds between requests
"""
import json, re, requests, time

with open('.env', 'r', encoding='utf-8') as f:
    env = {}
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k] = v

WB_KEY = env['WB_API_KEY']
H = {'Authorization': WB_KEY, 'Content-Type': 'application/json'}

with open('wb_cards_seo_dump.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

# ===== CHARACTERISTIC DEFAULTS BY SUBJECT =====
CHAR_DEFAULTS = {
    201: {  # Браслеты
        'Пол': ['Унисекс'],
        'Тип подарка': ['подарок — украшение', 'памятный подарок'],
        'Назначение': ['повседневный аксессуар'],
        'Вид браслета': ['жёсткий'],
        'Страна производства': ['Россия'],
        'Повод': ['день рождения', 'просто так', 'новый год', '14 февраля', '23 февраля', '8 марта'],
        'Назначение подарка': ['для мужчины', 'для женщины'],
    },
    297: {  # Брелоки
        'Ставка НДС': ['Без НДС'],
        'Тип подарка': ['подарок — аксессуар', 'памятный подарок'],
        'Декоративные элементы': ['гравировка'],
        'Вид замка': ['карабин'],
        'Комплектация': ['Брелок в подарочной упаковке'],
        'Повод': ['день рождения', 'просто так'],
        'Назначение подарка': ['для мужчины', 'для женщины'],
        'Эффекты': ['без эффектов'],
        'Высота предмета': ['5'],
        'Ширина предмета': ['3'],
        'Количество предметов в упаковке': ['1'],
        'Назначение': ['для ключей'],
    },
    298: {  # Подвески
        'Покрытие': ['без покрытия'],
        'Тип подарка': ['подарок — украшение'],
        'Вид подвески': ['подвеска'],
        'Вставка': ['без вставки'],
        'Пол': ['Унисекс'],
        'Назначение подарка': ['для мужчины', 'для женщины'],
    }
}

# ===== TITLE IMPROVEMENT =====
ZODIAC_RU = {
    'овен': 'Овен', 'телец': 'Телец', 'близнец': 'Близнецы', 'рак': 'Рак',
    'лев': 'Лев', 'дев': 'Дева', 'весы': 'Весы', 'скорпион': 'Скорпион',
    'стрелец': 'Стрелец', 'козерог': 'Козерог', 'водолей': 'Водолей', 'рыб': 'Рыбы',
    'leo': 'Лев', 'aries': 'Овен', 'taurus': 'Телец', 'gemini': 'Близнецы',
    'cancer': 'Рак', 'virgo': 'Дева', 'libra': 'Весы', 'scorpio': 'Скорпион',
    'sagittarius': 'Стрелец', 'capricorn': 'Козерог', 'aquarius': 'Водолей', 'pisces': 'Рыбы'
}

def detect_zodiac(title):
    tl = title.lower()
    for key, name in ZODIAC_RU.items():
        if key in tl:
            return name
    return None

def improve_title(title):
    if len(title) >= 30:
        return None
    tl = title.lower().strip()
    zodiac = detect_zodiac(title)
    if tl == 'брелок для ключей':
        return "Брелок для ключей с гравировкой подарок из нержавеющей стали GRAVMIX"
    elif 'брелок' in tl:
        if len(title) < 20:
            return title + " с гравировкой подарок GRAVMIX из стали 316L"
        else:
            return title + " GRAVMIX из стали 316L"
    elif 'жетон' in tl:
        return title + " из нержавеющей стали GRAVMIX"
    elif zodiac and len(title) < 25:
        return f"Браслет с гравировкой знак зодиака {zodiac} талисман GRAVMIX из стали 316L"
    elif 'браслет' in tl:
        return title + " GRAVMIX из нержавеющей стали 316L"
    else:
        return title + " GRAVMIX из стали 316L"

# ===== DESCRIPTION EXPANSION =====
def expand_description(title, old_desc):
    if len(old_desc) >= 500:
        return None
    parts = []
    if len(old_desc) > 100:
        parts.append(old_desc.rstrip('.') + '.')
    if '316l' not in old_desc.lower() and 'нержавеющ' not in old_desc.lower():
        parts.append("Изделие выполнено из высококачественной нержавеющей стали 316L — гипоаллергенного материала хирургического класса. Не темнеет, не ржавеет, не оставляет следов на коже и абсолютно не боится воды.")
    if 'браслет' in title.lower() and 'размер' not in old_desc.lower():
        parts.append("Универсальный размер: длина браслета легко регулируется от 14 до 22 см.")
    if 'гравировк' not in old_desc.lower():
        parts.append("Качественная лазерная гравировка не стирается и не тускнеет со временем.")
    if 'упаковк' not in old_desc.lower():
        parts.append("Поставляется в подарочной упаковке — бархатном мешочке, полностью готово к вручению.")
    zodiac = detect_zodiac(title)
    if zodiac:
        parts.append(f"Стильный аксессуар со знаком зодиака {zodiac} — талисман на удачу.")
    parts.append("Отличный подарок на день рождения, 23 февраля, 8 марта или просто как знак внимания. Бренд GRAVMIX гарантирует премиальное качество каждого изделия.")
    return " ".join(parts)

# ===== COLLECT ALL UPDATES =====
print("Analyzing cards...")
updates = []

for c in cards:
    nmID = c['nmID']
    vc = c['vendorCode']
    title = c['title']
    desc = c['description']
    sizes = c.get('sizes', [])
    sid = c.get('subjectID')
    chars = c.get('characteristics', [])
    
    needs_update = False
    new_title = None
    new_desc = None
    new_chars = list(chars)
    
    # 1. Check missing characteristics
    if sid in CHAR_DEFAULTS:
        existing_names = set(ch.get('name', '') for ch in chars)
        for char_name, default_val in CHAR_DEFAULTS[sid].items():
            if char_name not in existing_names:
                # Find the characteristic ID from other cards with same subject
                char_id = None
                for c2 in cards:
                    if c2.get('subjectID') == sid:
                        for ch2 in c2.get('characteristics', []):
                            if ch2.get('name') == char_name:
                                char_id = ch2.get('id')
                                break
                    if char_id:
                        break
                
                if char_id:
                    new_chars.append({'id': char_id, 'name': char_name, 'value': default_val if isinstance(default_val, list) else [default_val]})
                    needs_update = True
    
    # 2. Check short title
    new_title = improve_title(title)
    if new_title:
        needs_update = True
    
    # 3. Check short description
    new_desc = expand_description(title, desc)
    if new_desc:
        needs_update = True
    
    if needs_update:
        update = {
            "nmID": nmID,
            "vendorCode": vc,
            "sizes": sizes,
            "characteristics": new_chars,
        }
        if new_title:
            update["title"] = new_title
        if new_desc:
            update["description"] = new_desc
        
        updates.append({
            'body': update,
            'vc': vc,
            'has_chars': len(new_chars) > len(chars),
            'has_title': new_title is not None,
            'has_desc': new_desc is not None,
        })

char_fixes = sum(1 for u in updates if u['has_chars'])
title_fixes = sum(1 for u in updates if u['has_title'])
desc_fixes = sum(1 for u in updates if u['has_desc'])
print(f"Updates prepared: {len(updates)}")
print(f"  Characteristics fixes: {char_fixes}")
print(f"  Title fixes: {title_fixes}")
print(f"  Description fixes: {desc_fixes}")

# ===== APPLY =====
ok = 0
err = 0
rate_limited = 0

for i, u in enumerate(updates):
    body = [u['body']]
    try:
        r = requests.post('https://content-api.wildberries.ru/content/v2/cards/update', headers=H, json=body, timeout=15)
        if r.status_code == 200 and not r.json().get('error'):
            ok += 1
        elif r.status_code == 429:
            rate_limited += 1
            time.sleep(10)  # Wait longer on rate limit
            # Retry
            r2 = requests.post('https://content-api.wildberries.ru/content/v2/cards/update', headers=H, json=body, timeout=15)
            if r2.status_code == 200 and not r2.json().get('error'):
                ok += 1
                rate_limited -= 1
            else:
                err += 1
                if err <= 3:
                    print(f"  ERR (retry) [{u['vc']}]: {r2.status_code} {r2.text[:80]}")
        else:
            err += 1
            if err <= 5:
                print(f"  ERR [{u['vc']}]: {r.status_code} {r.text[:100]}")
    except Exception as e:
        err += 1
        print(f"  Exception: {str(e)[:50]}")
    
    if (i + 1) % 10 == 0:
        print(f"  progress: {i+1}/{len(updates)} ok:{ok} err:{err} rl:{rate_limited}")
    time.sleep(3)

print(f"\nDONE: {ok} updated, {err} errors, {rate_limited} rate limited")
