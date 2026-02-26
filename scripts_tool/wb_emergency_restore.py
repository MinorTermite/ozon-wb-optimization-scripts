# -*- coding: utf-8 -*-
"""
WB Emergency Restore:
1. Include full 'dimensions' object (5x5x2 cm, 0.05 kg) and 'sizes'
2. Fix numeric characteristics requiring integer values instead of strings
3. Re-apply SEO fixes (titles, descriptions, defaults)
4. Apply to ALL 266 cards to ensure draft cleanup
"""
import json, requests, time

with open('.env', 'r', encoding='utf-8') as f:
    env = {}
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k] = v

WB_KEY = env['WB_API_KEY']
H = {'Authorization': WB_KEY, 'Content-Type': 'application/json'}

# Always use our pristine backup as the source of truth
with open('wb_cards_seo_dump.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

CHAR_DEFAULTS = {
    201: {
        'Пол': ['Унисекс'], 'Тип подарка': ['подарок — украшение', 'памятный подарок'],
        'Назначение': ['повседневный аксессуар'], 'Вид браслета': ['жёсткий'],
        'Страна производства': ['Россия'],
        'Повод': ['день рождения', 'просто так', 'новый год', '14 февраля', '23 февраля', '8 марта'],
        'Назначение подарка': ['для мужчины', 'для женщины'],
    },
    297: {
        'Ставка НДС': ['Без НДС'], 'Тип подарка': ['подарок — аксессуар', 'памятный подарок'],
        'Декоративные элементы': ['гравировка'], 'Вид замка': ['карабин'],
        'Комплектация': ['Брелок в подарочной упаковке'], 'Повод': ['день рождения', 'просто так'],
        'Назначение подарка': ['для мужчины', 'для женщины'], 'Эффекты': ['без эффектов'],
        'Высота предмета': [5], 'Ширина предмета': [3], 'Количество предметов в упаковке': [1],
        'Назначение': ['для ключей'],
    },
    298: {
        'Покрытие': ['без покрытия'], 'Тип подарка': ['подарок — украшение'],
        'Вид подвески': ['подвеска'], 'Вставка': ['без вставки'], 'Пол': ['Унисекс'],
        'Назначение подарка': ['для мужчины', 'для женщины'],
    }
}

NUMERIC_FIELDS = {'Ширина предмета', 'Высота предмета', 'Длина предмета', 
                  'Количество предметов в упаковке', 'Ширина упаковки', 
                  'Высота упаковки', 'Длина упаковки', 'Вес товара с упаковкой (г)'}

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
        if key in tl: return name
    return None

def improve_title(title):
    if len(title) >= 30: return title
    tl = title.lower().strip()
    zodiac = detect_zodiac(title)
    if tl == 'брелок для ключей':
        return "Брелок для ключей с гравировкой подарок из нержавеющей стали GRAVMIX"
    elif 'брелок' in tl:
        return title + (" с гравировкой подарок GRAVMIX из стали 316L" if len(title) < 20 else " GRAVMIX из стали 316L")
    elif 'жетон' in tl:
        return title + " из нержавеющей стали GRAVMIX"
    elif zodiac and len(title) < 25:
        return f"Браслет с гравировкой знак зодиака {zodiac} талисман GRAVMIX из стали 316L"
    elif 'браслет' in tl:
        return title + " GRAVMIX из нержавеющей стали 316L"
    else:
        return title + " GRAVMIX из стали 316L"

def expand_description(title, old_desc):
    if len(old_desc) >= 500: return old_desc
    parts = []
    if len(old_desc) > 100: parts.append(old_desc.rstrip('.') + '.')
    if '316l' not in old_desc.lower() and 'нержавеющ' not in old_desc.lower():
        parts.append("Изделие выполнено из высококачественной нержавеющей стали 316L — гипоаллергенного материала хирургического класса. Не темнеет, не ржавеет, не оставляет следов на коже и не боится воды.")
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

updates = []

for c in cards:
    nmID = c['nmID']
    vc = c['vendorCode']
    title = improve_title(c['title'])
    desc = expand_description(c['title'], c['description'])
    sizes = c.get('sizes', [])
    sid = c.get('subjectID')
    chars = c.get('characteristics', [])
    
    # Process characteristics
    new_chars = []
    existing_names = set()
    
    for ch in chars:
        name = ch.get('name', '')
        val = ch.get('value', [])
        
        # Cast numeric fields to ints
        if name in NUMERIC_FIELDS and val is not None:
            new_val = []
            if not isinstance(val, list):
                val_list = [val]
            else:
                val_list = val
                
            for v in val_list:
                try:
                    new_val.append(int(float(v)))
                except (ValueError, TypeError):
                    new_val.append(v)
            new_chars.append({'id': ch['id'], 'name': name, 'value': new_val})
        else:
            new_chars.append(ch)
        existing_names.add(name)
        
    # Add defaults
    if sid in CHAR_DEFAULTS:
        for char_name, default_val in CHAR_DEFAULTS[sid].items():
            if char_name not in existing_names:
                char_id = None
                # find id from other cards
                for c2 in cards:
                    if c2.get('subjectID') == sid:
                        for ch2 in c2.get('characteristics', []):
                            if ch2.get('name') == char_name:
                                char_id = ch2.get('id')
                                break
                    if char_id: break
                
                if char_id:
                    new_chars.append({'id': char_id, 'name': char_name, 'value': default_val})
    
    update = {
        "nmID": nmID,
        "vendorCode": vc,
        "title": title,
        "description": desc,
        "sizes": sizes,
        "characteristics": new_chars,
        "dimensions": {
            "width": 5,      # As requested by user
            "height": 2,     # As requested by user
            "length": 5,     # As requested by user
            "weightBrutto": 0.05,
            "isValid": True
        }
    }
    updates.append(update)

print(f"Prepared full restoration updates for {len(updates)} cards.")

# Execute!
ok = 0
err = 0
for i, u in enumerate(updates):
    body = [u]
    try:
        r = requests.post('https://content-api.wildberries.ru/content/v2/cards/update', headers=H, json=body, timeout=15)
        if r.status_code == 200 and not r.json().get('error'):
            ok += 1
        elif r.status_code == 429:
            time.sleep(10)
            r2 = requests.post('https://content-api.wildberries.ru/content/v2/cards/update', headers=H, json=body, timeout=15)
            if r2.status_code == 200 and not r2.json().get('error'):
                ok += 1
            else:
                err += 1
                if err <= 5: print(f"  ERR [{u['vendorCode']}]: {r2.status_code} {r2.text[:80]}")
        else:
            err += 1
            if err <= 5: print(f"  ERR [{u['vendorCode']}]: {r.status_code} {r.text[:100]}")
    except Exception as e:
        err += 1
    
    if (i + 1) % 20 == 0:
        print(f"  progress: {i+1}/{len(updates)} ok:{ok} err:{err}")
    time.sleep(1)

print(f"\nDONE: {ok} restored, {err} errors")
