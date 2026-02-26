# -*- coding: utf-8 -*-
import json, requests, time

# Load env
with open('.env', 'r', encoding='utf-8') as f:
    env = dict(line.strip().split('=', 1) for line in f if '=' in line and not line.startswith('#'))

H = {'Authorization': env['WB_API_KEY'], 'Content-Type': 'application/json'}

# Source of truth: Original Backup
with open('wb_cards_seo_dump.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

# Categories Mapping for filling missing fields
# subjectID: defaults
CAT_DEFAULTS = {
    201: { # Браслеты
        'Тип подарка': ['подарок — украшение', 'памятный подарок'],
        'Назначение': ['повседневный аксессуар'], 'Вид браслета': ['жёсткий'],
        'Страна производства': ['Россия'],
        'Повод': ['день рождения', 'просто так', 'новый год', '14 февраля', '23 февраля', '8 марта'],
        'Назначение подарка': ['для мужчины', 'для женщины'],
    },
    297: { # Брелоки
        'Ставка НДС': ['Без НДС'], 'Тип подарка': ['подарок — аксессуар', 'памятный подарок'],
        'Декоративные элементы': ['гравировка'], 'Вид замка': ['карабин'],
        'Комплектация': ['Брелок в подарочной упаковке'], 'Повод': ['день рождения', 'просто так'],
        'Назначение подарка': ['для мужчины', 'для женщины'], 'Эффекты': ['без эффектов'],
        'Высота предмета': 5, 'Ширина предмета': 3, 'Количество предметов в упаковке': ['1 шт.'],
        'Назначение': ['для ключей'],
    },
    298: { # Подвески бижутерные
        'Покрытие': ['без покрытия'], 'Тип подарка': ['подарок — украшение'],
        'Вид подвески': ['подвеска'], 'Вставка': ['без вставки'],
        'Назначение подарка': ['для мужчины', 'для женщины'],
    }
}

# Fields that MUST BE NAKED INTEGERS (no array, no string) based on check_dump_types result
STRICT_NUMERIC = {'Ширина предмета', 'Высота предмета', 'Длина предмета'}

# SEO Tools
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
    if len(title) > 50: return title
    tl = title.lower().strip()
    zodiac = detect_zodiac(title)
    
    new_t = title
    if tl == 'брелок для ключей':
        new_t = "Брелок с гравировкой сталь GRAVMIX"
    elif 'брелок' in tl:
        new_t = title + " сталь GRAVMIX"
    elif 'жетон' in tl:
        new_t = title + " сталь GRAVMIX"
    elif zodiac:
        new_t = f"Браслет {zodiac} сталь GRAVMIX"
    elif 'браслет' in tl:
        new_t = title + " сталь GRAVMIX"
    else:
        new_t = title + " GRAVMIX"
        
    return new_t[:60].strip()

def expand_description(title, old_desc):
    if len(old_desc) >= 500: return old_desc
    parts = ["Изделие выполнено из высококачественной нержавеющей стали 316L — гипоаллергенного материала хирургического класса. Не темнеет, не ржавеет, не оставляет следов на коже и не боится воды."]
    if 'браслет' in title.lower():
        parts.append("Универсальный размер: длина браслета легко регулируется от 14 до 22 см.")
    if 'гравировк' not in old_desc.lower():
        parts.append("Качественная лазерная гравировка не стирается и не тускнеет со временем.")
    parts.append("Поставляется в подарочной упаковке — бархатном мешочке, полностью готово к вручению.")
    zodiac = detect_zodiac(title)
    if zodiac:
        parts.append(f"Стильный аксессуар со знаком зодиака {zodiac} — талисман на удачу.")
    parts.append("Отличный подарок на день рождения, 23 февраля, 8 марта или просто как знак внимания. Бренд GRAVMIX гарантирует премиальное качество каждого изделия.")
    return " ".join(parts)

# Pre-fetch all IDs to avoid missing them
ID_MAP = {}
for c in cards:
    sid = c.get('subjectID')
    if sid not in ID_MAP: ID_MAP[sid] = {}
    for ch in c.get('characteristics', []):
        ID_MAP[sid][ch['name']] = ch['id']

updates = []
for c in cards:
    nmID = c['nmID']
    vc = c['vendorCode']
    sid = c.get('subjectID')
    
    # SEO
    title = improve_title(c['title'])
    desc = expand_description(c['title'], c['description'])
    
    # Characteristics
    old_chars = c.get('characteristics', [])
    new_chars = []
    seen = set()
    
    # 1. Process old chars with TYPE FIXES
    for ch in old_chars:
        name = ch['name']
        val = ch['value']
        
        # FIX GENDER (Пол)
        if name == 'Пол' and val == ['Унисекс']:
            # Fallback to original dump value or logic
            if 'муж' in title.lower() or 'пап' in title.lower() or 'дед' in title.lower() or 'сын' in title.lower() or 'брат' in title.lower():
                val = ['Мужской']
            elif 'жен' in title.lower() or 'мам' in title.lower() or 'бабу' in title.lower() or 'доч' in title.lower() or 'сест' in title.lower():
                val = ['Женский']
            else:
                val = ['Женский'] # WB often requires Gender for jewelry, default safely
        
        if name in STRICT_NUMERIC:
            # FORCE SINGLE INT
            try:
                new_val = int(float(val[0])) if isinstance(val, list) and val else int(float(val))
                new_chars.append({"id": ch['id'], "name": name, "value": new_val})
            except:
                new_chars.append({"id": ch['id'], "name": name, "value": val}) # fallback
        else:
            new_chars.append({"id": ch['id'], "name": name, "value": val})
        seen.add(name)
        
    # 2. Add defaults for category
    if sid in CAT_DEFAULTS:
        for name, val in CAT_DEFAULTS[sid].items():
            if name not in seen:
                char_id = ID_MAP.get(sid, {}).get(name)
                if char_id:
                    # Apply numeric type for new chars too
                    if name in STRICT_NUMERIC and isinstance(val, list):
                        try: final_val = int(float(val[0]))
                        except: final_val = val
                    else:
                        final_val = val
                    new_chars.append({"id": char_id, "name": name, "value": final_val})
    
    update = {
        "nmID": nmID,
        "vendorCode": vc,
        "title": title,
        "description": desc,
        "sizes": c.get('sizes', []),
        "characteristics": new_chars,
        "dimensions": {
            "width": 5, "height": 2, "length": 5,
            "weightBrutto": 0.05, "isValid": True
        }
    }
    updates.append(update)

print(f"Total updates prepared: {len(updates)}")

# Execute in batches
ok = 0
err = 0
BATCH_SIZE = 50

for i in range(0, len(updates), BATCH_SIZE):
    batch = updates[i:i+BATCH_SIZE]
    try:
        r = requests.post('https://content-api.wildberries.ru/content/v2/cards/update', headers=H, json=batch, timeout=30)
        
        # Handle 429 (Too Many Requests)
        if r.status_code == 429:
            print(f"  Got 429. Sleeping 60s...")
            time.sleep(60)
            r = requests.post('https://content-api.wildberries.ru/content/v2/cards/update', headers=H, json=batch, timeout=30)

        if r.status_code == 200 and not r.json().get('error'):
            ok += len(batch)
            print(f"  Success batch {i//BATCH_SIZE + 1}. Progress: {min(i+BATCH_SIZE, len(updates))}/{len(updates)}")
        else:
            err += len(batch)
            print(f"  ERR batch {i//BATCH_SIZE + 1}: {r.status_code} {r.text[:200]}")
    except Exception as e:
        err += len(batch)
        print(f"  Exception: {str(e)}")
        
    time.sleep(3) # Safer delay

print(f"\nFINISH: {ok} OK, {err} ERR")
